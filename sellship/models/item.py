import re

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models


class Originality(models.TextChoices):
    OEM = 'OEM', 'OEM'
    NOT_OEM = 'NOT OEM', 'NOT OEM'


class Brand(models.TextChoices):
    YAMAHA = 'YAMAHA', 'YAMAHA'
    QUICKSILVER = 'QUICKSILVER', 'QUICKSILVER'
    MERCRUISER = 'MERCRUISER', 'MERCRUISER'
    MERCURY = 'MERCURY', 'MERCURY'
    HONDA = 'HONDA', 'HONDA'
    KAWASAKI = 'KAWASAKI', 'KAWASAKI'
    SUZUKI = 'SUZUKI', 'SUZUKI'
    POLARIS = 'POLARIS', 'POLARIS'
    TOYOTA = 'TOYOTA', 'TOYOTA'
    VOLKSWAGEN = 'VOLKSWAGEN', 'VOLKSWAGEN'
    VOLVO = 'VOLVO', 'VOLVO'
    AUDI = 'AUDI', 'AUDI'
    BMW = 'BMW', 'BMW'
    MERCEDES = 'MERCEDES', 'MERCEDES'
    MASERATO = 'MASERATO', 'MASERATO'
    NISSAN = 'NISSAN', 'NISSAN'
    AUTOBAHN = 'AUTOBAHN', 'AUTOBAHN'
    ARCTIC_CAT = 'ARCTIC CAT', 'ARCTIC CAT'



class TransportType(models.TextChoices):
    KATER = "КАТЕР", "КАТЕР"
    AUTO = "АВТО", "АВТО"
    SNEGOHOD = "СНЕГОХОД", "СНЕГОХОД"

def validate_article_format(value):
    pattern = re.compile(r'^[A-Z0-9\-]+$')  # только A-Z, 0-9 и тире
    invalid_items = [item for item in value if not pattern.match(item)]
    if invalid_items:
        raise ValidationError(
            f"Недопустимые значения в 'article': {invalid_items}. "
            "Разрешены только большие буквы A-Z, цифры 0-9 и тире '-'."
        )


class Item(models.Model):
    id = models.CharField(max_length=15, primary_key=True, db_column='smart', verbose_name="ID")
    name = models.CharField(max_length=100, db_column="наименование", blank=True, verbose_name="Наименование")
    originality = models.CharField(max_length=7, choices=Originality.choices, db_column="оригинальность", null=False,
                                   verbose_name="Оригинальность")
    brand = ArrayField(models.CharField(max_length=15, choices=Brand.choices, null=False), size=10, default=list,
                       db_column="бренд", verbose_name="Бренд")
    connect_brand = ArrayField(models.CharField(max_length=15, choices=Brand.choices), size=10, default=list,
                               db_column="коннект_бренд", blank=True, verbose_name="Коннект бренд")
    transport_type = ArrayField(models.CharField(max_length=15, choices=TransportType.choices), size=6, default=list,
                                db_column="тип_транспорта", verbose_name="Тип транспорта")
    area_usage = ArrayField(models.CharField(max_length=20), size=5, default=list, db_column="область_применения",
                            blank=True, verbose_name="Область применения")
    weight = models.FloatField(default=0, db_column="вес", blank=True, verbose_name="Вес")
    volume = models.FloatField(default=0, db_column="объем", blank=True, verbose_name="Объем")
    article = ArrayField(models.CharField(max_length=20, null=False), default=list, db_column="артикул",
                         validators=[validate_article_format], verbose_name="Артикул")
    connect_article = ArrayField(models.CharField(max_length=20), default=list, db_column="коннект_артикул", blank=True,
                                 validators=[validate_article_format], verbose_name="Коннект артикул")

    #ФУНКЦИЯ ДЛЯ ПРОВЕРКИ УНИКАЛЬНОСТИ ЗНАЧЕНИЙ ПО НЕСКОЛЬКИМ ЯЧЕЙКАМ
    def clean(self):
        super().clean()
        fields_to_check = ['article', 'connect_article', 'brand', 'connect_brand']

        combined = []
        for field_name in fields_to_check:
            values = getattr(self, field_name)
            if values:
                combined.extend(values)

        duplicates = [x for x in set(combined) if combined.count(x) > 1]

        if duplicates:
            raise ValidationError('Значения должны быть уникальны в brand, connect_brand, article, connect_article')



    class Meta:
        db_table = "smart"
        verbose_name = "Запчасть"
        verbose_name_plural = "Запчасти"

    def __str__(self):
        return f"<{self._meta.verbose_name}: {self.pk}>"
