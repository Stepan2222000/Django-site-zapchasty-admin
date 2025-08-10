from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.fields import CharField
from django.utils import timezone


class Market(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=250)



class StatusType(models.TextChoices):
    CLOSED = "ЗАКРЫТО", "ЗАКРЫТО"
    OVERED = "ЗАВЕРШЕНО", "ЗАВЕРШЕНО"
    PURCHASED = "КУПЛЕННО", "КУПЛЕННО"
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

class CurrencyChoices(models.TextChoices):
    USD = 'USD', 'USD'
    EURO = 'EURO', 'EURO'


class PriorityChoices(models.TextChoices):
    HIGH = "high", "High"
    MEDIUM = "medium", "Medium"
    LOW = "low", "Low"


class EbayShippingInfo(models.Model):
    number_announcement = models.BigIntegerField(validators=[MinValueValidator(100000000000), MaxValueValidator(999999999999)], db_column="номер_объявления", verbose_name="Номер объявления")
    smart = models.ForeignKey("Item", on_delete=models.CASCADE, db_column='smart', verbose_name="Товар")
    max_price = models.IntegerField(blank=True, db_column="максимальная_цена", verbose_name="Максимальная цена")
    priority = models.CharField(default=PriorityChoices.LOW, choices=PriorityChoices.choices, verbose_name="Приоритет", db_column="приоритет")
    account_ebay = models.CharField(choices=AccountEbayChoices.choices, null=False, db_column="аккаунт_ебей", default=AccountEbayChoices.kensinerjack, verbose_name="Аккаунт eBay")
    status = models.CharField(max_length=9, choices=StatusType.choices, null=False, db_column="статус", default=StatusType.PURCHASED, verbose_name="Статус")
    last_updated_status = models.DateTimeField(default=timezone.now, db_column="последнее_обновление_статуса", null=True, blank=True, verbose_name="Последнее обновление статуса")
    seller_name = models.CharField(max_length=100, db_column="имя_продавца", verbose_name="Имя продавца")
    shipping_type = models.CharField(max_length=5, choices=ShippingType.choices, null=False, db_column="тип_доставки", default=ShippingType.AIR, verbose_name="Тип доставки")
    final_price = models.FloatField(db_column="финальная_цена", verbose_name="Финальная цена")
    overhead = models.FloatField(default=0, db_column="дополнительные_затраты", verbose_name="Дополнительные затраты")
    shipper = models.CharField(max_length=100, choices=ShipperChoices.choices, null=False, blank=False, db_column="отправщик", default=ShipperChoices.EVGENIY, verbose_name="Отправщик")
    track_number = models.CharField(max_length=150, db_column="трек", null=True, blank=True, verbose_name="Трек-номер")
    date_arrive = models.DateField(db_column="дата_прихода_на_склад", null=True, blank=True, verbose_name="Дата прихода на склад")
    country = models.CharField(max_length=100, choices=CountryChoices.choices, null=False, blank=False, db_column="страна_склада", default=CountryChoices.USA, verbose_name="Страна склада")
    comments = models.TextField(db_column="коментарий", verbose_name="Комментарий")
    order_link = models.URLField(max_length=256, db_column="ссылка_заказ", verbose_name="Ссылка на заказ")
    rf_send = models.BooleanField(db_column="рф_отправленно", verbose_name="Отправлено в РФ")
    date_list_create = models.DateField("Дата создания листа", null=True, blank=True)
    currency = models.CharField(max_length=10, choices=CurrencyChoices.choices, default=CurrencyChoices.USD, db_column="валюта", verbose_name="Валюта")

    class Meta:
        verbose_name = "Информация о доставке eBay"
        verbose_name_plural = "Информация о доставке eBay"

    def __str__(self):
        return f"<{self._meta.verbose_name}: {self.pk}>"
