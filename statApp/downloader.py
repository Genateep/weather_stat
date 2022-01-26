import os
from datetime import date, timedelta

import dotenv
import requests
from django.core.exceptions import ObjectDoesNotExist

from .models import CityList, OneDayData

CITIES = [
        'Moscow',
        'Saint Petersburg',
        'Novosibirsk',
        'Ekaterinburg',
        'Kazan',
        'Nizhniy Novgorod',
        'Chelyabinsk',
        'Samara',
        'Vladivostok',
        'Murmansk',
        'Helsinki',
        'Minsk',
        'Berlin',
        'Paris',
        'London'
    ]


def download_from_wwo(enddate=date.today()):
    """checks db and gets updates from api"""

    try:  # checks db for last entry to start from
        latest_saved = OneDayData.objects.latest('id').date
    except ObjectDoesNotExist:
        latest_saved = date(2010, 1, 1)

    if latest_saved == enddate:
        return
    elif latest_saved == date(2010, 1, 1):
        startdate = latest_saved
    else:
        startdate = latest_saved + timedelta(1)

    def requester(cityname, start, end):
        link = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
        dotenv.load_dotenv(dotenv.find_dotenv())
        wwo_api_key = os.environ['WWO_API']

        payload = {
            "q": cityname,
            "tp": '24',
            "date": start,
            "enddate": end,
            "format": "json",
            "key": wwo_api_key
        }
        response = requests.get(link, params=payload)
        return response.json()['data']['weather']

    def downloader(start, end):

        for c in CITIES:  # upd list of cities
            CityList.objects.get_or_create(city=c)

        for obj in CityList.objects.all():
            city = str(obj)

            try:
                weather = requester(city, start, end)
            except KeyError:  # in case of empty response at start of the day
                end -= timedelta(1)
                weather = requester(city, start, end)

            for day in weather:
                o = OneDayData(
                    city=obj,
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

    # worldweatheronline-api provides up to 35 days data in one request only
    if (enddate - startdate).days <= 35:
        return downloader(startdate, enddate)
    elif (enddate - startdate).days > 35:
        while startdate < (enddate - timedelta(35)):
            downloader(startdate, enddate)
            startdate += timedelta(35)
        downloader(startdate, enddate)
