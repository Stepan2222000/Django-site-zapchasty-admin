import re
from subprocess import check_output

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint
from django.db.models.expressions import RawSQL
from django.db.models.fields import CharField, URLField
from django.utils import timezone


# Create your models here.

class Originality(models.TextChoices):
    OEM = 'OEM', 'OEM'
    NOT_OEM = 'NOT OEM', 'NOT OEM'


class Brand(models.TextChoices):
    YAMAHA = 'YAMAHA', 'YAMAHA'
    QUICKSILVER = 'QUICKSILVER', 'QUICKSILVER'
    MERCRUISER = 'MERCRUISER', 'MERCRUISER'
    MERCURY = 'MERCURY', 'MERCURY'


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


    id = models.CharField(
        max_length=15,
        primary_key=True,
        db_column='smart',
    )

    name = models.CharField(max_length=100, db_column="наименование", blank=True)
    originality = models.CharField(max_length=7, choices=Originality.choices, db_column="оригинальность", null=False)
    brand = ArrayField(models.CharField(max_length=15 ,choices=Brand.choices, null=False),  size=10, default=list, db_column="бренд")
    connect_brand = ArrayField(models.CharField(max_length=15, choices=Brand.choices),  size=10, default=list, db_column="коннект_бренд", blank=True)
    transport_type = ArrayField(models.CharField(max_length=15, choices=TransportType.choices),  size=6, default=list, db_column="тип_транспорта")
    area_usage = ArrayField(models.CharField(max_length=20), size=5, default=list, db_column="область_применения", blank=True)
    weight = models.FloatField(default=0, db_column="вес", blank=True)
    volume = models.FloatField(default=0, db_column="объем", blank=True)
    article = ArrayField(models.CharField(max_length=20, null=False), default=list, db_column="артикул", validators=[validate_article_format])
    connect_article = ArrayField(models.CharField(max_length=20), default=list, db_column="коннект_артикул", blank=True, validators=[validate_article_format])

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




# ---------------------------

class Market(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=250)



class StatusType(models.TextChoices):
    CLOSED = "ЗАКРЫТО", "КАТЕР"
    OVERED = "ЗАВЕРШЕНО", "АВТО"
    PURCHASED = "КУПЛЕННО", "СНЕГОХОД"
    OFFERED = "ОФФЕР", "ОФФЕР"
    WRITTEN = "НАПИСАЛИ", "НАПИСАЛИ"
    COLLECTED =  "СОБРАННО", "СОБРАННО"
    MISTAKES =  "ОШИБКИ", "ОШИБКИ"

class ShippingType(models.TextChoices):
    AIR = "АВИА", "АВИА"
    SEA = "МОРЕМ", "МОРЕМ"




class ShipperChoices(models.TextChoices):
    EVGENIY = "ЕВГЕНИЙ_ДЕЛАВЕР", "ЕВГЕНИЙ ДЕЛАВЕР"
    KIRGIZIA = "КИРГИЗИЯ_ДЕЛАВЕР", "КИРГИЗИЯ ДЕЛАВЕР"

class CountryChoices(models.TextChoices):
    USA = "США", "США"
    GERMANY = "ГЕРАМНИЯ", "ГЕРАМНИЯ"

class AccountEbayChoices(models.TextChoices):
    kensinerjack = "kensinerjack", "kensinerjack"
    prom = "prom", "prom"


class EbayShippingInfo(models.Model):
     number_announcement = models.BigIntegerField(
        validators=[
            MinValueValidator(100000000000),
            MaxValueValidator(999999999999)  # 12 цифр
        ], db_column="номер_объявления"
     )
     smart = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='smart')

     max_price = models.IntegerField(blank=True, db_column="максимальная_цена")
     account_ebay = models.CharField(choices=AccountEbayChoices.choices, null=False, db_column="аккаунт_ебей")
     status = models.CharField(max_length=9, choices=StatusType.choices, null=False, db_column="статус")
     last_updated_status = models.DateTimeField(default=timezone.now, db_column="последнее_обновление_статуса")
     seller_name = CharField(max_length=100, db_column="имя_продавца")
     shipping_type = models.CharField(max_length=5, choices=ShippingType.choices, null=False, db_column="тип_доставки")
     final_price = models.FloatField(db_column="финальная_цена")
     overhead = models.FloatField(default=0, db_column="дополнительные_затраты")
     shipper = models.CharField(max_length=100, choices=ShipperChoices.choices, null=False, db_column="отправщик")
     track_number = models.CharField(max_length=150, db_column="трек", null=True, blank=True)
     date_arrive = models.DateField(db_column="дата_прихода_на_склад", null=True, blank=True)
     country = models.CharField(max_length=100, choices=CountryChoices.choices, null=False, blank=False, db_column="страна_склада")
     comments = models.TextField(db_column="коментарий")
     order_link = models.URLField(max_length=256, db_column="ссылка_заказ")
     rf_send = models.BooleanField(db_column="рф_отправленно")
     date_list_create = models.DateField("дата_создания_листа")



















