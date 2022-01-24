from django.contrib import admin

from .models import CityList, OneDayData


@admin.register(OneDayData)
class WeatherAdmin(admin.ModelAdmin):
    pass


@admin.register(CityList)
class CityAdmin(admin.ModelAdmin):
    pass
