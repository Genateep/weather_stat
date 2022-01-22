import datetime

from django.db import models

import requests
from datetime import date, timedelta


class OneDayData(models.Model):
    city = models.CharField(max_length=30)
    date = models.DateField()
    maxTemp = models.SmallIntegerField()
    minTemp = models.SmallIntegerField()
    avgTemp = models.SmallIntegerField()
    windSpeed = models.SmallIntegerField()
    windDir = models.CharField(max_length=3)
    precipitation = models.DecimalField(max_digits=4, decimal_places=1)
    desc = models.CharField(max_length=40)

    def __str__(self):
        return self.city


def get_info_from_site(city='Moscow', startdate='2021-01-01', enddate=str(date.today())):
    link = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
    wwo_api_key = '469327e52a7d4df9b31102143222101'

    startdate = date(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:]))
    enddate = date(int(enddate[:4]), int(enddate[5:7]), int(enddate[8:]))

    def downloader(startdate, enddate):
        payload = {
            "q": city,
            "tp": '24',
            "date": startdate,
            "enddate": enddate,
            "format": "json",
            "key": wwo_api_key
        }
        response = requests.get(link, params=payload)
        for day in response.json()['data']['weather']:
            o = OneDayData(
                city=city,
                date=day['date'],
                maxTemp=day['maxtempC'],
                minTemp=day['mintempC'],
                avgTemp=day['avgtempC'],
                windSpeed=day['hourly'][0]['windspeedKmph'],
                windDir=day['hourly'][0]['winddir16Point'],
                precipitation=day['hourly'][0]['precipMM'],
                desc=day['hourly'][0]['weatherDesc'][0]['value']
            )
            o.save()

    if (enddate - startdate).days <= 35:
        return downloader(startdate, enddate)
    elif (enddate - startdate).days > 35:
        while startdate < (enddate - timedelta(35)):
            downloader(startdate, enddate)
            startdate += timedelta(35)
        downloader(startdate, enddate)


get_info_from_site()
