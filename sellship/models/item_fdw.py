from django.contrib.postgres.fields import ArrayField
from django.db import models

from sellship.models import Brand, TransportType, validate_article_format


class ItemFDW(models.Model):
    """
    Unmanaged модель для foreign table smart из default БД через postgres_fdw.
    Используется для связи EbayShippingInfo с Item через разные БД.
    """
    id = models.CharField(max_length=50, primary_key=True, db_column='smart', verbose_name="ID")
    name = models.CharField(max_length=100, db_column="наименование", blank=True, verbose_name="Наименование")
    originality = models.CharField(max_length=7, db_column="оригинальность", null=False, verbose_name="Оригинальность")
    brand = ArrayField(models.CharField(max_length=20, choices=Brand.choices, null=False), size=10, default=list,
                       db_column="бренд", verbose_name="Бренд")
    connect_brand = ArrayField(models.CharField(max_length=20, choices=Brand.choices), size=10, default=list,
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

    class Meta:
        managed = False  # Django не будет управлять этой таблицей
        db_table = '"default_fdw"."smart"'   # foreign table через postgres_fdw
        app_label = "sellship"
        verbose_name = "Запчасть (FDW)"
        verbose_name_plural = "Запчасти (FDW)"

    def __str__(self):
        return f"<{self._meta.verbose_name}: {self.pk}>"


