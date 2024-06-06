from django.db import models
import requests
from rest_framework import serializers

from transport.models import City, Company, CompanyBlockList, CompanyNumber, ZipCode, CompanyDocument, StockImage, Country

class CheckLoadUnloadSerializer(serializers.Serializer):
    country = serializers.IntegerField(required=True, allow_null=True)
    city = serializers.IntegerField(required=True, allow_null=True)
    zip_code = serializers.IntegerField(required=True, allow_null=True)
    start_datetime = serializers.DateTimeField(required=True, allow_null=True)
    end_datetime = serializers.DateTimeField(required=True, allow_null=True)
    type = serializers.CharField(required=True)

class CheckCargoNoteSerializer(serializers.Serializer):
    lang = serializers.CharField(required=True)
    cargo_note = serializers.CharField(required=False, allow_blank=True)

class CheckVehicleNoteSerializer(serializers.Serializer):
    lang = serializers.CharField(required=True)
    vehicle_note = serializers.CharField(required=False, allow_blank=True)

class CheckCargoSerializer(serializers.Serializer):
    length = serializers.FloatField(required=True, allow_null=True)
    width = serializers.FloatField(required=True, allow_null=True)
    weight = serializers.FloatField(required=True, allow_null=True)
    cargo_note = CheckCargoNoteSerializer(many=True, required=False)
    price = serializers.FloatField(required=True, allow_null=True)
    exchange = serializers.BooleanField(required=True)
    goods_types = serializers.ListField(required=False)

class CheckVehicleSerializer(serializers.Serializer):
    vehicle_types = serializers.ListField(required=True)
    vehicle_upgrades = serializers.ListField(required=True)
    vehicle_equipment = serializers.ListField(required=True)
    contact_accounts = serializers.ListField(required=True)
    vehicle_note = CheckVehicleNoteSerializer(many=True, required=False)

class CheckAuctionSerializer(serializers.Serializer):
    auction = serializers.BooleanField(required=True)
    start_price = serializers.FloatField(required=True, allow_null=True)
    auction_end_datetime = serializers.DateTimeField(required=True, allow_null=True)
    min_down_bind_percentage = serializers.DecimalField(max_digits=4, decimal_places=1, allow_null=True)

class CheckInsertCargoSerializer(serializers.Serializer):
    load_unload = CheckLoadUnloadSerializer(many=True)
    cargo = CheckCargoSerializer()
    vehicle = CheckVehicleSerializer()
    auction = CheckAuctionSerializer()

class CheckUpdateCargoSerializer(serializers.Serializer):
    load_unload = CheckLoadUnloadSerializer(many=True)
    cargo = CheckCargoSerializer()
    vehicle = CheckVehicleSerializer()
    auction = CheckAuctionSerializer()
    cargo_id = serializers.IntegerField(allow_null=False)

class CheckInsertAuctionSerializer(serializers.Serializer):
    cargo = serializers.IntegerField(required=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    
class CheckInsertLoadingSpaceVehicleSerializer(serializers.Serializer):
    vehicle_type = serializers.IntegerField(required=True, allow_null=True)
    vehicle_length = serializers.DecimalField(required=True, max_digits=6, decimal_places=2, allow_null=True)
    vehicle_upgrades = serializers.ListField(required=True, allow_null=True)
    vehicle_equipment = serializers.ListField(required=True, allow_null=True)
    contact_accounts = serializers.ListField(required=True, allow_null=True)
    vehicle_load_capacity = serializers.DecimalField(required=True, max_digits=11, decimal_places=2, allow_null=True)
    connected_vehicle_length = serializers.DecimalField(required=True, max_digits=6, decimal_places=2, allow_null=True)
    connected_vehicle_load_capacity = serializers.DecimalField(required=True, max_digits=11, decimal_places=2, allow_null=True)
    vehicle_note = CheckVehicleNoteSerializer(many=True, allow_null=True)

class CheckInsertStartingPointDestination(serializers.Serializer):
    country = serializers.IntegerField(required=True, allow_null=True)
    city = serializers.IntegerField(required=True, allow_null=True)
    zip_code = serializers.IntegerField(required=True, allow_null=True)
    departure_datetime = serializers.DateTimeField(required=False, allow_null=True)
    within_km = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.CharField(required=True)

class CheckInsertLoadingSpaceSerializer(serializers.Serializer):
    vehicle = CheckInsertLoadingSpaceVehicleSerializer()
    starting_point_destination = CheckInsertStartingPointDestination(many=True)

class CheckUpdateLoadingSpaceSerializer(serializers.Serializer):
    loading_space_id = serializers.IntegerField(required=True)
    vehicle = CheckInsertLoadingSpaceVehicleSerializer()
    starting_point_destination = CheckInsertStartingPointDestination(many=True)

class CheckStockSerializer(serializers.Serializer):
    country = serializers.IntegerField(required=True, allow_null=True)
    city = serializers.IntegerField(required=True, allow_null=True)
    zip_code = serializers.IntegerField(required=True, allow_null=True)
    start_datetime = serializers.DateTimeField(required=True, allow_null=True)
    end_datetime = serializers.DateTimeField(required=True, allow_null=True)
    min_area = serializers.DecimalField(required=True, max_digits=11, decimal_places=2, allow_null=True)
    max_area = serializers.DecimalField(required=True, max_digits=11, decimal_places=2, allow_null=True)
    stock_types = serializers.CharField(required=True, allow_blank=True)
    stock_equipment = serializers.CharField(required=True, allow_blank=True)
    contact_accounts = serializers.ListField(required=True, allow_null=True)

class CheckInsertStockSerializer(serializers.Serializer):
    stock = CheckStockSerializer()

class CheckUpdateStockSerializer(serializers.Serializer):
    stock = CheckStockSerializer()
    stock_id = serializers.IntegerField(required=True)

class CheckBlockCompanySerializer(serializers.Serializer):
    block = serializers.BooleanField(required=True)
    company = serializers.IntegerField(required=True)


class CheckGetCitiesByCountrySerializer(serializers.Serializer):
    country = serializers.IntegerField(required=True)

class CheckGetZipCodesByCitySerializer(serializers.Serializer):
    city = serializers.IntegerField(required=True)

class CheckCompanyServicesSerializer(serializers.Serializer):
    goods_forms = serializers.ListField()
    goods_types = serializers.ListField()
    transport_types = serializers.ListField()
    own_vehicles = serializers.BooleanField(required=True)
    vehicles_num = serializers.IntegerField(required=True, allow_null=True)
    vehicle_types = serializers.ListField()
    vehicle_upgrades = serializers.ListField()
    loading_systems = serializers.ListField()



class CheckUpdateCompanySerializer(serializers.Serializer):
    company_name = serializers.CharField(required=True, allow_blank=True)
    company_emails = serializers.ListField()
    company_country = serializers.IntegerField(required=True, allow_null=True)
    company_city = serializers.IntegerField(required=True, allow_null=True)
    company_zip_code = serializers.IntegerField(required=True, allow_null=True)
    company_OIB = serializers.CharField(required=True, allow_blank=True)
    company_year = serializers.CharField(required=True, allow_blank=True)
    company_web = serializers.CharField(required=True, allow_blank=True)
    company_numbers = serializers.ListField()
    company_services = CheckCompanyServicesSerializer()



class CheckConfirmCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)
    confirm = serializers.BooleanField(required=True)



class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'OIB', 'address'
        )

class CompanyNumbersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyNumber
        fields = (
            'id',
            'number',
            'type'
        )

class CompanyDetailsSerializer(serializers.ModelSerializer):
    company_numbers = CompanyNumbersSerializer(many=True)
    class Meta:
        model = Company
        fields = (
            'id', 
            'name', 
            'OIB', 
            'address',
            'web',
            'year',
            'company_numbers',
            'company_emails'
        )

class UpdateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id', 
            'name', 
            'OIB', 
            'address',
            'web',
            'year',
            'country',
            'city',
            'zip_code'
        )

class ListCompanyBlockSerializer(serializers.ModelSerializer):
    blocked_company = CompanyListSerializer()
    class Meta:
        model = CompanyBlockList
        fields = ('id', 'blocked_company', 'blocked_by')

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')

class InsertCitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'country')

class InsertZipCodeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='code', read_only=True)
    class Meta:
        model = ZipCode
        fields = ('id', 'name', 'code', 'city')

class ListCitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'country_id')

class ListZipCodesSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='code')
    class Meta:
        model = ZipCode
        fields = ('id', 'name', 'code', 'city_id')

class CompanyDocumentsSerializer(serializers.ModelSerializer):
    path = serializers.CharField(source='path.name')
    class Meta:
        model = CompanyDocument
        fields = (
            'id', 'title', 'path'
        )

class StockImagesSerializer(serializers.ModelSerializer):
    path = serializers.CharField(source='path.name')
    class Meta:
        model = StockImage
        fields = (
            'id', 'title', 'path'
        )