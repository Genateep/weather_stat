import datetime
import os
import requests

from datetime import date, timedelta
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class CityList(models.Model):
    city = models.CharField(max_length=30, verbose_name='Название города')

    def __str__(self):
        return self.city


class OneDayData(models.Model):
    city = models.ForeignKey(CityList, null=True, blank=True, default=None, on_delete=models.CASCADE)
    date = models.DateField()
    maxTemp = models.SmallIntegerField()
    minTemp = models.SmallIntegerField()
    avgTemp = models.SmallIntegerField()
    windSpeed = models.SmallIntegerField()
    windDir = models.CharField(max_length=3)
    precipitation = models.DecimalField(max_digits=4, decimal_places=1)
    desc = models.CharField(max_length=40)

    def __str__(self):
        return self.desc
