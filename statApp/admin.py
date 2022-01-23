from django.contrib import admin
from .models import *


@admin.register(OneDayData)
class WeatherAdmin(admin.ModelAdmin):
    pass


@admin.register(CityList)
class WeatherAdmin(admin.ModelAdmin):
    pass
