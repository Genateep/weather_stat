import datetime
import os
import requests

from datetime import date, timedelta
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class CityList(models.Model):
    city = models.CharField(max_length=255, verbose_name='Название города')

    def __str__(self):
        return self.city


class OneDayData(models.Model):
    # city = models.CharField(max_length=30)
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


# cities = [
#         'Moscow',
#         'Saint Petersburg',
#         'Novosibirsk',
#         'Ekaterinburg',
#         'Kazan',
#         'Nizhniy Novgorod',
#         'Chelyabinsk',
#         'Samara',
#         'Omsk',
#         'Rostov-on-don',
#         'Helsinki',
#         'Minsk',
#         'Berlin',
#         'Paris',
#         'London'
#     ]
#
#
# def get_info_from_site(cities, enddate=date.today()):
#     link = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
#     # wwo_api_key = os.environ.get('WWO_API2')
#     wwo_api_key = '6ac29886d0fd4305ac7131306222201'
#
#     # startdate = date(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:]))
#     # enddate = date(int(enddate[:4]), int(enddate[5:7]), int(enddate[8:]))
#
#     try:
#         latest_saved = OneDayData.objects.latest('id').date
#     except ObjectDoesNotExist:
#         latest_saved = date(2010, 1, 1)
#
#     if latest_saved == enddate:
#         return
#     elif latest_saved == date(2010, 1, 1):
#         startdate = latest_saved
#     else:
#         startdate = latest_saved + timedelta(1)
#
#     def downloader(cities, startdate, enddate):
#         for city in cities:
#             payload = {
#                 "q": city,
#                 "tp": '24',
#                 "date": startdate,
#                 "enddate": enddate,
#                 "format": "json",
#                 "key": wwo_api_key
#             }
#             response = requests.get(link, params=payload)
#             for day in response.json()['data']['weather']:
#                 o = OneDayData(
#                     city=city,
#                     date=day['date'],
#                     maxTemp=day['maxtempC'],
#                     minTemp=day['mintempC'],
#                     avgTemp=day['avgtempC'],
#                     windSpeed=day['hourly'][0]['windspeedKmph'],
#                     windDir=day['hourly'][0]['winddir16Point'],
#                     precipitation=day['hourly'][0]['precipMM'],
#                     desc=day['hourly'][0]['weatherDesc'][0]['value']
#                 )
#                 o.save()
#
#     if (enddate - startdate).days <= 35:
#         return downloader(cities, startdate, enddate)
#     elif (enddate - startdate).days > 35:
#         while startdate < (enddate - timedelta(35)):
#             downloader(cities, startdate, enddate)
#             startdate += timedelta(35)
#         downloader(cities, startdate, enddate)
#
#
# get_info_from_site(cities)
