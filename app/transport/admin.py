from django.contrib import admin
from .models import *


# Register your models here.

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

class CargoAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction')

class LoadingSpaceAdmin(admin.ModelAdmin):
    list_display = ('id', )

class StockAdmin(admin.ModelAdmin):
    list_display = ('id', )

admin.site.register(Company, CompanyAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(LoadingSpace, LoadingSpaceAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(ZipCode)