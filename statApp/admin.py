from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(OneDayData)
class WeatherAdmin(admin.ModelAdmin):
    pass


@admin.register(CityList)
class WeatherAdmin(admin.ModelAdmin):
    pass
