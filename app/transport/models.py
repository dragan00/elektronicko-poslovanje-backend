from django.db import models

import accounts.models
from .constants import *
from .managers import *
from django.db.models import Q

LANG_CHOICES = [
    (HR, 'Hrvatski'),
    (EN, 'Engleski')
]

STATUS_CHOICES = [
    (ACTIVE, ACTIVE),
    (CLOSED, CLOSED)
]

# ABSTRACT START

class Translation(models.Model):
    lang = models.CharField(max_length=6, choices=LANG_CHOICES, blank=True, null=True, default=None)
    name = models.CharField(max_length=256, blank=True, null=True, default=None)

    class Meta:
        abstract = True


class CreatorAbstract(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, blank=True, null=True, default=None,
                                   related_name='created_by')

    class Meta:
        abstract = True

class CloseAbstract(models.Model):
    closed_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        abstract = True


# ABSTRACT END

class Language(models.Model):
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=50, blank=True, null=True, default=None)
    alpha2Code = models.CharField(max_length=4, blank=True, null=True, default=None)

    def __str__(self):
        return f'{self.name} ({self.native_name})'


class Country(models.Model):
    name = models.CharField(max_length=256)
    alpha2Code = models.CharField(max_length=4, blank=True, null=True, default=None)
    alpha3Code = models.CharField(max_length=6, blank=True, null=True, default=None)
    translations = models.JSONField(blank=True, null=True, default=None)
    flag = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)

    @property
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class City(models.Model):
    name = models.CharField(max_length=256)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ZipCode(models.Model):
    code = models.CharField(max_length=30)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['code']


class GoodsForm(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class TransportType(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class LoadingSystem(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class VehicleEquipment(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class Company(models.Model):

    COMPANY_STATUS_CHOICES = [
        (ACTIVE, ACTIVE),
        (NEED_CONFIRM, NEED_CONFIRM),
        (REJECTED, REJECTED)
    ]

    number = models.IntegerField(blank=True, null=True, default=None)
    name = models.CharField(max_length=256)
    OIB = models.CharField(max_length=256, blank=True, null=True, default=None)
    web = models.CharField(max_length=256, blank=True, null=True, default=None)
    avatar = models.ImageField(blank=True, null=True, default=None, upload_to='images/')
    address = models.CharField(max_length=512, blank=True, null=True, default=None)
    year = models.IntegerField(blank=True, null=True, default=None)
    creator = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name='creator', blank=True,
                                null=True, default=None)
    cover_countries = models.ManyToManyField(Country, blank=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=None,
                                related_name='company_country')
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, default=None,
                             related_name='company_city')
    zip_code = models.ForeignKey(ZipCode, on_delete=models.CASCADE, blank=True, null=True, default=None,
                                 related_name='company_zip_code')
    goods_forms = models.ManyToManyField(GoodsForm, blank=True)
    goods_types = models.ManyToManyField("GoodsType", blank=True)
    transport_types = models.ManyToManyField(TransportType, blank=True)
    # storage_posibility = #TODO O ovom cemo pricat i ovom dole vehicle_equipment
    own_vehicles = models.BooleanField(blank=True, null=True, default=None)
    vehicles_num = models.IntegerField(blank=True, null=True, default=None)
    vehicle_types = models.ManyToManyField("VehicleType", blank=True)
    vehicle_upgrades = models.ManyToManyField("VehicleUpgrade", blank=True)
    # vehicle_features = models.ManyToManyField("VehicleFeature", blank=True)
    loading_systems = models.ManyToManyField(LoadingSystem, blank=True)
    vehicle_equipment = models.ManyToManyField(VehicleEquipment, blank=True)
    status = models.CharField(max_length=15, choices=COMPANY_STATUS_CHOICES, blank=True, null=True, default=NEED_CONFIRM)
    confirmed_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name='confirmed_by', blank=True,
                                null=True, default=None)
    confirmed_at = models.DateTimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(blank=True, null=True, default=None)

    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    details = CompanyDetailsManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class CompanyDocument(models.Model):
    title = models.TextField(blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    path = models.FileField(upload_to='files/')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_documents')
    is_active = models.BooleanField(default=True)

class CompanyMail(models.Model):
    email = models.EmailField(verbose_name="email", max_length=80)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_emails')


class CompanyNumber(models.Model):
    number = models.CharField(max_length=30, blank=True, null=True, default=None)
    type = models.CharField(max_length=20, blank=True, null=True, default=None)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_numbers')


class CompanyService(models.Model):
    description = models.TextField(blank=True, null=True, default=None)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    lang = models.CharField(max_length=4, choices=LANG_CHOICES, default=HR)


class CompanyBlockList(models.Model):
    my_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='my_company')
    blocked_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='blocked_company')
    blocked_at = models.DateTimeField(auto_now_add=True)
    unblocked_at = models.DateTimeField(blank=True, null=True, default=None)
    blocked_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name='blocked_by')
    unblocked_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, blank=True, null=True, default=None,
                                     related_name='unblocked_by')


class VehicleType(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class VehicleTypeTranslate(Translation, models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)


class VehicleUpgrade(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class VehicleUpgradeTranslate(Translation, models.Model):
    vehicle_upgrade = models.ForeignKey(VehicleUpgrade, on_delete=models.CASCADE)


class VehicleFeature(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class VehicleFeatureTranslate(Translation, models.Model):
    vehicle_feature = models.ForeignKey(VehicleFeature, on_delete=models.CASCADE)


class GoodsType(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class GoodsTypeTranslate(Translation, models.Model):
    goods_type = models.ForeignKey(GoodsType, on_delete=models.CASCADE)


class Cargo(CreatorAbstract, CloseAbstract, models.Model):
    length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=None)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=None)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=None)
    cargo_note = models.JSONField(blank=True, null=True, default=None)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=None)
    exchange = models.BooleanField(default=False)
    goods_types = models.ManyToManyField(GoodsType, blank=True)
    vehicle_types = models.ManyToManyField(VehicleType, blank=True)
    vehicle_upgrades = models.ManyToManyField(VehicleUpgrade, blank=True)
    vehicle_features = models.ManyToManyField(VehicleFeature, blank=True)
    vehicle_equipment = models.ManyToManyField(VehicleEquipment, blank=True)
    contact_accounts = models.ManyToManyField("accounts.Account", blank=True)
    vehicle_note = models.JSONField(blank=True, null=True, default=None)
    auction = models.BooleanField(default=False)
    auction_end_datetime = models.DateTimeField(blank=True, null=True, default=None)
    auction_notification_sent = models.BooleanField(blank=True, null=True, default=False)
    min_down_bind_percentage = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, default=None)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, blank=True, null=True, default=ACTIVE)

    def get_last_bid(self):
        try:
            print(self.cargo.filter(~Q(account=self.created_by)).order_by('-id')[0])
            return self.cargo.filter(~Q(account=self.created_by)).order_by('-id')[0]
        except:
            return None

class Auction(models.Model):
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='cargo')
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class CargoLoadUnload(models.Model):
    TYPE_CHOICES = [
        (LOAD, 'Utovar'),
        (UNLOAD, 'Istovar')
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=None)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, default=None)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.CASCADE, blank=True, null=True, default=None)
    start_datetime = models.DateTimeField(blank=True, null=True, default=None)
    end_datetime = models.DateTimeField(blank=True, null=True, default=None)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, blank=True, null=True, default=None)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)


class LoadingSpace(CloseAbstract, models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, blank=True, null=True, default=None)
    vehicle_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=None)
    vehicle_upgrades = models.ManyToManyField(VehicleUpgrade, blank=True)
    vehicle_features = models.ManyToManyField(VehicleFeature, blank=True)
    vehicle_equipment = models.ManyToManyField(VehicleEquipment, blank=True)
    contact_accounts = models.ManyToManyField("accounts.Account", blank=True,
                                              related_name='loading_space_contact_accounts')
    vehicle_load_capacity = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True, default=None)
    connected_vehicle_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=None)
    connected_vehicle_load_capacity = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True,
                                                          default=None)
    vehicle_note = models.JSONField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, blank=True, null=True, default=None)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, default=None)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, blank=True, null=True, default=ACTIVE)


class StartingPointDestination(models.Model):
    TYPE_CHOICES = [
        (STARTING, 'Polazište'),
        (DESTINATION, 'Odredište')
    ]
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=None)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, default=None)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.CASCADE, blank=True, null=True, default=None)
    departure_datetime = models.DateTimeField(blank=True, null=True, default=None)
    within_km = models.IntegerField(blank=True, null=True, default=None)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, blank=True, null=True, default=None)
    loading_space = models.ForeignKey(LoadingSpace, on_delete=models.CASCADE)


class StockType(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class StockEquipment(models.Model):
    name = models.JSONField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)


class Stock(CloseAbstract, models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=None)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, default=None)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.CASCADE, blank=True, null=True, default=None)
    start_datetime = models.DateTimeField(blank=True, null=True, default=None)
    end_datetime = models.DateTimeField(blank=True, null=True, default=None)
    min_area = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True, default=None)
    max_area = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True, default=None)
    # stock_types = models.ManyToManyField(StockType, blank=True)
    # stock_equipments = models.ManyToManyField(StockEquipment, blank=True)
    stock_types = models.TextField(blank=True, null=True, default=None)
    stock_equipment = models.TextField(blank=True, null=True, default=None)
    contact_accounts = models.ManyToManyField("accounts.Account", blank=True, related_name='stock_contact_accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, blank=True, null=True, default=None)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, blank=True, null=True, default=ACTIVE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, default=None)


class StockImage(models.Model):
    title = models.TextField(blank=True, null=True, default=None)
    path = models.ImageField(upload_to='images/')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True, default=None)
    is_active = models.BooleanField(blank=True, null=True, default=True)
