"""
Management command для импорта артикулов из Excel файла в модель Item.

Использование:
    python manage.py import_articles /path/to/file.xlsx
    python manage.py import_articles /path/to/file.xlsx --dry-run
    python manage.py import_articles /path/to/file.xlsx --limit 100
"""

import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import pandas as pd

from sellship.models import Item, Brand


# Словарь синонимов брендов
BRAND_SYNONYMS = {
    'BENZ': 'MERCEDES',
    'MERCEDES BENZ': 'MERCEDES',
    'DAIMLER': 'MERCEDES',
    'DAIMLER AG': 'MERCEDES',
    'VAG': 'VOLKSWAGEN',
    'VWGROUP': 'VOLKSWAGEN',
    'FOMOCO': 'FORD',
    'FEBI BILSTEIN': 'FEBI',
    'KNECHTMAHLE': 'KNECHT',
    'BEHR HELLA SERVICE': 'BEHR',
    'SALERISIL': 'SALERI',
    'KAYABA': 'KYB',
    'ROBERT BOSCH GMBH': 'BOSCH',
    'GKN (LOEBRO)': 'GKN',
}

# Бренды для разделения
BRANDS_TO_SPLIT = {
    'TOYOTALEXUS': ['TOYOTA', 'LEXUS'],
    'HYUNDAI KIA': ['HYUNDAI', 'KIA'],
}

# Паттерн для валидации артикулов
ARTICLE_PATTERN = re.compile(r'^[A-Z0-9\-]+$')

# Паттерн для научной нотации (испорченные Excel)
SCIENTIFIC_PATTERN = re.compile(r'^[\d]+,[\d]+E[+\-]\d+$')


class Command(BaseCommand):
    help = 'Импортирует артикулы из Excel файла в модель Item'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Путь к Excel файлу')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только проверка без записи в БД',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Ограничить количество импортируемых записей (0 = без ограничения)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Размер пакета для bulk_create (по умолчанию 1000)',
        )

    def get_valid_brands(self):
        """Получить множество валидных брендов из модели"""
        return {choice[0] for choice in Brand.choices}

    def get_last_smart_number(self):
        """Получить последний номер smart_ из БД"""
        last_item = Item.objects.filter(id__startswith='smart_').order_by('-id').first()
        if last_item:
            try:
                num = int(last_item.id.replace('smart_', ''))
                return num
            except ValueError:
                pass
        return 0

    def normalize_brand(self, brand):
        """Нормализовать бренд: применить синонимы, разделить составные"""
        brand = brand.strip().upper()

        # Разделить составные бренды
        if brand in BRANDS_TO_SPLIT:
            return BRANDS_TO_SPLIT[brand]

        # Применить синонимы
        if brand in BRAND_SYNONYMS:
            brand = BRAND_SYNONYMS[brand]

        return [brand]

    def process_brands(self, brands_str, valid_brands):
        """Обработать строку брендов из Excel"""
        result = []
        unknown = []

        for brand in str(brands_str).split(','):
            normalized = self.normalize_brand(brand)
            for b in normalized:
                if b in valid_brands:
                    if b not in result:  # Избегаем дубликатов
                        result.append(b)
                else:
                    if b not in unknown:
                        unknown.append(b)

        return result, unknown

    def is_valid_article(self, article):
        """Проверить валидность артикула"""
        art = str(article)

        # Проверить научную нотацию
        if SCIENTIFIC_PATTERN.match(art):
            return False, 'scientific_notation'

        # Проверить длину (max 15 для id)
        if len(art) > 15:
            return False, 'too_long'

        # Проверить паттерн
        if not ARTICLE_PATTERN.match(art):
            return False, 'invalid_pattern'

        return True, None

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        dry_run = options['dry_run']
        limit = options['limit']
        batch_size = options['batch_size']

        self.stdout.write(f'Загрузка файла: {excel_file}')

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            raise CommandError(f'Ошибка загрузки Excel: {e}')

        self.stdout.write(f'Загружено строк: {len(df)}')

        # Получить валидные бренды
        valid_brands = self.get_valid_brands()
        self.stdout.write(f'Валидных брендов в модели: {len(valid_brands)}')

        # Получить последний номер
        last_num = self.get_last_smart_number()
        self.stdout.write(f'Последний smart номер в БД: {last_num}')

        # Статистика
        stats = {
            'total': len(df),
            'processed': 0,
            'skipped_scientific': 0,
            'skipped_too_long': 0,
            'skipped_invalid': 0,
            'skipped_duplicate': 0,
            'skipped_no_brands': 0,
            'created': 0,
            'unknown_brands': set(),
        }

        # Отслеживание дубликатов
        seen_articles = set()

        # Список для bulk_create
        items_to_create = []
        current_num = last_num

        # Ограничить если нужно
        if limit > 0:
            df = df.head(limit)
            self.stdout.write(f'Ограничено до {limit} записей')

        for idx, row in df.iterrows():
            article = str(row['articulum'])
            brands_str = row['brands']

            # Проверить дубликаты
            if article in seen_articles:
                stats['skipped_duplicate'] += 1
                continue
            seen_articles.add(article)

            # Проверить валидность артикула
            is_valid, reason = self.is_valid_article(article)
            if not is_valid:
                if reason == 'scientific_notation':
                    stats['skipped_scientific'] += 1
                elif reason == 'too_long':
                    stats['skipped_too_long'] += 1
                else:
                    stats['skipped_invalid'] += 1
                continue

            # Обработать бренды
            processed_brands, unknown = self.process_brands(brands_str, valid_brands)
            stats['unknown_brands'].update(unknown)

            if not processed_brands:
                stats['skipped_no_brands'] += 1
                continue

            # Создать запись
            current_num += 1
            smart_id = f'smart_{current_num:05d}'

            item = Item(
                id=smart_id,
                name='',
                originality='OEM',
                brand=processed_brands,
                connect_brand=[],
                transport_type=['АВТО'],
                area_usage=[],
                weight=0,
                volume=0,
                article=[article],
                connect_article=[],
            )

            items_to_create.append(item)
            stats['processed'] += 1

            # Bulk create по пакетам
            if len(items_to_create) >= batch_size:
                if not dry_run:
                    with transaction.atomic():
                        Item.objects.bulk_create(items_to_create)
                    stats['created'] += len(items_to_create)
                    self.stdout.write(f'Создано: {stats["created"]} записей...')
                items_to_create = []

        # Создать оставшиеся
        if items_to_create:
            if not dry_run:
                with transaction.atomic():
                    Item.objects.bulk_create(items_to_create)
                stats['created'] += len(items_to_create)

        # Вывод статистики
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('СТАТИСТИКА ИМПОРТА')
        self.stdout.write('=' * 50)
        self.stdout.write(f"Всего строк в файле: {stats['total']}")
        self.stdout.write(f"Обработано успешно: {stats['processed']}")
        self.stdout.write(f"Пропущено (научная нотация): {stats['skipped_scientific']}")
        self.stdout.write(f"Пропущено (слишком длинные): {stats['skipped_too_long']}")
        self.stdout.write(f"Пропущено (невалидный формат): {stats['skipped_invalid']}")
        self.stdout.write(f"Пропущено (дубликаты): {stats['skipped_duplicate']}")
        self.stdout.write(f"Пропущено (нет известных брендов): {stats['skipped_no_brands']}")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: записи НЕ созданы"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nСоздано записей: {stats['created']}"))

        if stats['unknown_brands']:
            self.stdout.write(f"\nНеизвестные бренды ({len(stats['unknown_brands'])}):")
            for brand in sorted(stats['unknown_brands'])[:50]:
                self.stdout.write(f"  - {brand}")
            if len(stats['unknown_brands']) > 50:
                self.stdout.write(f"  ... и ещё {len(stats['unknown_brands']) - 50}")
