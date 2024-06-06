from .models import *
from rest_framework import serializers
from django.core.exceptions import PermissionDenied
from transport.models import Company

class CheckUpdatePanesSerializer(serializers.Serializer):
    # account = serializers.IntegerField(required=True)
    panes = serializers.JSONField(required=True)

class BasicCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name')

class CheckCompanyServicesSerializer(serializers.Serializer):
    goods_forms = serializers.ListField()
    goods_types = serializers.ListField()
    transport_types = serializers.ListField()
    own_vehicles = serializers.BooleanField(required=True)
    vehicles_num = serializers.IntegerField(required=True, allow_null=True)
    vehicle_types = serializers.ListField()
    vehicle_upgrades = serializers.ListField()
    loading_systems = serializers.ListField()


class CheckRegisterAccountSerializer(serializers.Serializer):
    account_full_name = serializers.CharField(required=True, allow_blank=True)
    account_password = serializers.CharField(required=False, allow_blank=True)
    account_email = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    account_phone_number = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    account_languages = serializers.ListField()


class CheckRegisterCompanySerializer(CheckRegisterAccountSerializer, serializers.Serializer):
    company = serializers.IntegerField(required=True, allow_null=True)
    company_name = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    company_emails = serializers.ListField()
    company_country = serializers.IntegerField(required=True, allow_null=True)
    company_city = serializers.IntegerField(required=True, allow_null=True)
    company_zip_code = serializers.IntegerField(required=True, allow_null=True)
    company_OIB = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    company_year = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    company_web = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    company_numbers = serializers.ListField()
    company_services = CheckCompanyServicesSerializer(required=False)
    company_cover_countries = serializers.ListField(required=False)


class CheckRemoveAccountSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'id', 'name', 'email', 'is_admin', 'phone_number', 'address')

class BackofficeAccountSerializer(serializers.ModelSerializer):
    company = BasicCompanySerializer()
    class Meta:
        model = Account
        fields = (
            'id', 'name', 'email', 'is_admin', 'phone_number', 'address', 'company')

class UpdateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'name', 'phone_number', 'languages'
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('old_password', 'new_password')

    # def validate(self, attrs):
    #     if attrs['password'] != attrs['password2']:
    #         raise serializers.ValidationError({"password": "Password fields didn't match."})
    #
    #     return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        print(user.id)
        print(value)
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        if self.context['request'].user != instance:
            raise PermissionDenied
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance
