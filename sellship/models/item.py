import re

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models


class Originality(models.TextChoices):
    OEM = 'OEM', 'OEM'
    NOT_OEM = 'NOT OEM', 'NOT OEM'


class Brand(models.TextChoices):
    # === СУЩЕСТВУЮЩИЕ (18) ===
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

    # === VOLKSWAGEN GROUP ===
    PORSCHE = 'PORSCHE', 'PORSCHE'
    SKODA = 'SKODA', 'SKODA'
    SEAT = 'SEAT', 'SEAT'
    BENTLEY = 'BENTLEY', 'BENTLEY'
    LAMBORGHINI = 'LAMBORGHINI', 'LAMBORGHINI'
    BUGATTI = 'BUGATTI', 'BUGATTI'

    # === BMW GROUP ===
    MINI = 'MINI', 'MINI'
    ROLLS_ROYCE = 'ROLLS ROYCE', 'ROLLS ROYCE'

    # === MERCEDES GROUP ===
    AMG = 'AMG', 'AMG'
    MAYBACH = 'MAYBACH', 'MAYBACH'
    SMART = 'SMART', 'SMART'

    # === STELLANTIS ===
    ALFA_ROMEO = 'ALFA ROMEO', 'ALFA ROMEO'
    CHRYSLER = 'CHRYSLER', 'CHRYSLER'
    CITROEN = 'CITROEN', 'CITROEN'
    DODGE = 'DODGE', 'DODGE'
    FIAT = 'FIAT', 'FIAT'
    JEEP = 'JEEP', 'JEEP'
    LANCIA = 'LANCIA', 'LANCIA'
    OPEL = 'OPEL', 'OPEL'
    PEUGEOT = 'PEUGEOT', 'PEUGEOT'
    RAM = 'RAM', 'RAM'
    VAUXHALL = 'VAUXHALL', 'VAUXHALL'

    # === GENERAL MOTORS ===
    CHEVROLET = 'CHEVROLET', 'CHEVROLET'
    CADILLAC = 'CADILLAC', 'CADILLAC'
    GMC = 'GMC', 'GMC'
    BUICK = 'BUICK', 'BUICK'

    # === FORD ===
    FORD = 'FORD', 'FORD'
    LINCOLN = 'LINCOLN', 'LINCOLN'

    # === TOYOTA GROUP ===
    LEXUS = 'LEXUS', 'LEXUS'
    DAIHATSU = 'DAIHATSU', 'DAIHATSU'
    HINO = 'HINO', 'HINO'

    # === HYUNDAI GROUP ===
    HYUNDAI = 'HYUNDAI', 'HYUNDAI'
    KIA = 'KIA', 'KIA'
    GENESIS = 'GENESIS', 'GENESIS'

    # === RENAULT-NISSAN-MITSUBISHI ===
    RENAULT = 'RENAULT', 'RENAULT'
    MITSUBISHI = 'MITSUBISHI', 'MITSUBISHI'
    INFINITI = 'INFINITI', 'INFINITI'
    DACIA = 'DACIA', 'DACIA'

    # === HONDA GROUP ===
    ACURA = 'ACURA', 'ACURA'

    # === JLR (TATA) ===
    JAGUAR = 'JAGUAR', 'JAGUAR'
    LAND_ROVER = 'LAND ROVER', 'LAND ROVER'
    RANGE_ROVER = 'RANGE ROVER', 'RANGE ROVER'

    # === НЕЗАВИСИМЫЕ ===
    MAZDA = 'MAZDA', 'MAZDA'
    SUBARU = 'SUBARU', 'SUBARU'
    ISUZU = 'ISUZU', 'ISUZU'
    SSANGYONG = 'SSANGYONG', 'SSANGYONG'
    SAAB = 'SAAB', 'SAAB'
    FERRARI = 'FERRARI', 'FERRARI'
    ASTON_MARTIN = 'ASTON MARTIN', 'ASTON MARTIN'

    # === КИТАЙСКИЕ ===
    FAW = 'FAW', 'FAW'
    CHANGAN = 'CHANGAN', 'CHANGAN'
    BAIC = 'BAIC', 'BAIC'
    GEELY = 'GEELY', 'GEELY'
    GREAT_WALL = 'GREAT WALL', 'GREAT WALL'
    HAVAL = 'HAVAL', 'HAVAL'
    CHERY = 'CHERY', 'CHERY'
    EXEED = 'EXEED', 'EXEED'
    JAC = 'JAC', 'JAC'
    LIFAN = 'LIFAN', 'LIFAN'
    LI_AUTO = 'LI AUTO', 'LI AUTO'
    CFMOTO = 'CFMOTO', 'CFMOTO'

    # === КОММЕРЧЕСКИЙ ТРАНСПОРТ ===
    MAN = 'MAN', 'MAN'
    SCANIA = 'SCANIA', 'SCANIA'
    IVECO = 'IVECO', 'IVECO'
    DAF = 'DAF', 'DAF'
    DAEWOO = 'DAEWOO', 'DAEWOO'

    # === POWERSPORTS / MARINE ===
    BRP = 'BRP', 'BRP'
    ROTAX = 'ROTAX', 'ROTAX'
    MERCURY_MARINE = 'MERCURY MARINE', 'MERCURY MARINE'

    # === AFTERMARKET - НЕМЕЦКИЕ TIER-1 ===
    BOSCH = 'BOSCH', 'BOSCH'
    CONTINENTAL = 'CONTINENTAL', 'CONTINENTAL'
    ZF_PARTS = 'ZF PARTS', 'ZF PARTS'
    SACHS = 'SACHS', 'SACHS'
    LEMFORDER = 'LEMFORDER', 'LEMFORDER'
    TRW = 'TRW', 'TRW'
    WABCO = 'WABCO', 'WABCO'
    INA = 'INA', 'INA'
    FAG = 'FAG', 'FAG'
    LUK = 'LUK', 'LUK'
    RUVILLE = 'RUVILLE', 'RUVILLE'
    MAHLE = 'MAHLE', 'MAHLE'
    KNECHT = 'KNECHT', 'KNECHT'
    BEHR = 'BEHR', 'BEHR'
    FEBI = 'FEBI', 'FEBI'
    SWAG = 'SWAG', 'SWAG'
    HELLA = 'HELLA', 'HELLA'
    MANN = 'MANN', 'MANN'
    HENGST = 'HENGST', 'HENGST'
    BILSTEIN = 'BILSTEIN', 'BILSTEIN'
    MEYLE = 'MEYLE', 'MEYLE'
    ELRING = 'ELRING', 'ELRING'
    KOLBENSCHMIDT = 'KOLBENSCHMIDT', 'KOLBENSCHMIDT'
    PIERBURG = 'PIERBURG', 'PIERBURG'
    BERU = 'BERU', 'BERU'
    WAHLER = 'WAHLER', 'WAHLER'
    ZIMMERMANN = 'ZIMMERMANN', 'ZIMMERMANN'

    # === AFTERMARKET - ЯПОНСКИЕ ===
    DENSO = 'DENSO', 'DENSO'
    AISIN = 'AISIN', 'AISIN'
    NGK = 'NGK', 'NGK'
    NTN = 'NTN', 'NTN'
    NSK = 'NSK', 'NSK'
    KOYO = 'KOYO', 'KOYO'
    AKEBONO = 'AKEBONO', 'AKEBONO'
    ADVICS = 'ADVICS', 'ADVICS'
    KYB = 'KYB', 'KYB'
    NISSIN = 'NISSIN', 'NISSIN'
    HITACHI = 'HITACHI', 'HITACHI'
    SANDEN = 'SANDEN', 'SANDEN'

    # === AFTERMARKET - АМЕРИКАНСКИЕ/ЕВРОПЕЙСКИЕ ===
    GATES = 'GATES', 'GATES'
    DAYCO = 'DAYCO', 'DAYCO'
    MONROE = 'MONROE', 'MONROE'
    DELPHI = 'DELPHI', 'DELPHI'
    BORGWARNER = 'BORGWARNER', 'BORGWARNER'
    GARRETT = 'GARRETT', 'GARRETT'
    HOLSET = 'HOLSET', 'HOLSET'
    IHI = 'IHI', 'IHI'
    VALEO = 'VALEO', 'VALEO'
    BREMBO = 'BREMBO', 'BREMBO'
    ATE = 'ATE', 'ATE'
    TEXTAR = 'TEXTAR', 'TEXTAR'
    FERODO = 'FERODO', 'FERODO'
    BENDIX = 'BENDIX', 'BENDIX'
    SKF = 'SKF', 'SKF'
    TIMKEN = 'TIMKEN', 'TIMKEN'
    GKN = 'GKN', 'GKN'
    MAGNETI_MARELLI = 'MAGNETI MARELLI', 'MAGNETI MARELLI'
    CORTECO = 'CORTECO', 'CORTECO'

    # === AFTERMARKET - КОРЕЙСКИЕ ===
    MOBIS = 'MOBIS', 'MOBIS'
    MANDO = 'MANDO', 'MANDO'

    # === МАСЛА И ЖИДКОСТИ ===
    CASTROL = 'CASTROL', 'CASTROL'
    MOBIL = 'MOBIL', 'MOBIL'
    SHELL = 'SHELL', 'SHELL'
    TOTAL = 'TOTAL', 'TOTAL'
    MOTUL = 'MOTUL', 'MOTUL'
    LIQUI_MOLY = 'LIQUI MOLY', 'LIQUI MOLY'
    FUCHS = 'FUCHS', 'FUCHS'
    RAVENOL = 'RAVENOL', 'RAVENOL'
    IDEMITSU = 'IDEMITSU', 'IDEMITSU'
    ZIC = 'ZIC', 'ZIC'
    PETRONAS = 'PETRONAS', 'PETRONAS'

    # === ШИНЫ ===
    MICHELIN = 'MICHELIN', 'MICHELIN'
    BRIDGESTONE = 'BRIDGESTONE', 'BRIDGESTONE'
    PIRELLI = 'PIRELLI', 'PIRELLI'

    # === СТЁКЛА ===
    FUYAO = 'FUYAO', 'FUYAO'
    AGC_AUTOMOTIVE = 'AGC AUTOMOTIVE', 'AGC AUTOMOTIVE'
    PILKINGTON = 'PILKINGTON', 'PILKINGTON'
    XYG = 'XYG', 'XYG'

    # === ПРОЧИЙ AFTERMARKET ===
    FEBEST = 'FEBEST', 'FEBEST'
    MASUMA = 'MASUMA', 'MASUMA'
    CTR = 'CTR', 'CTR'
    SIDEM = 'SIDEM', 'SIDEM'
    MAPCO = 'MAPCO', 'MAPCO'
    MAXGEAR = 'MAXGEAR', 'MAXGEAR'
    ZEKKERT = 'ZEKKERT', 'ZEKKERT'
    LYNX = 'LYNX', 'LYNX'
    LUZAR = 'LUZAR', 'LUZAR'
    KRAUF = 'KRAUF', 'KRAUF'
    NISSENS = 'NISSENS', 'NISSENS'
    HEPU = 'HEPU', 'HEPU'
    DOLZ = 'DOLZ', 'DOLZ'
    SALERI = 'SALERI', 'SALERI'
    GALFER = 'GALFER', 'GALFER'
    QUATTRO_FRENI = 'QUATTRO FRENI', 'QUATTRO FRENI'
    OSRAM = 'OSRAM', 'OSRAM'
    PHILIPS = 'PHILIPS', 'PHILIPS'
    EXIDE = 'EXIDE', 'EXIDE'
    AGM = 'AGM', 'AGM'
    VDO = 'VDO', 'VDO'
    SIEMENS = 'SIEMENS', 'SIEMENS'
    MOTORCRAFT = 'MOTORCRAFT', 'MOTORCRAFT'
    HIDRIA = 'HIDRIA', 'HIDRIA'
    CONTITECH = 'CONTITECH', 'CONTITECH'
    SNR = 'SNR', 'SNR'
    NOK = 'NOK', 'NOK'
    JURID = 'JURID', 'JURID'
    FILTRON = 'FILTRON', 'FILTRON'
    HANS_PRIES = 'HANS PRIES', 'HANS PRIES'
    VIKA = 'VIKA', 'VIKA'
    SAT = 'SAT', 'SAT'
    JRONE = 'JRONE', 'JRONE'
    JORDEN = 'JORDEN', 'JORDEN'
    METACO = 'METACO', 'METACO'
    DOMINANT = 'DOMINANT', 'DOMINANT'
    POLCAR = 'POLCAR', 'POLCAR'
    DAR = 'DAR', 'DAR'
    AFIRE = 'AFIRE', 'AFIRE'
    AAA = 'AAA', 'AAA'



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
