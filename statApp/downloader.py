from datetime import date, timedelta
import requests
import json
from .models import OneDayData, CityList
from django.core.exceptions import ObjectDoesNotExist

VC_KEY = 'CW9G58J7LK7BR6NJJW595YMPF'
wwo_api_key = 'f5a196eaccca4cfe84a191947222301'
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


# for city in CITIES:
#     c = CityList(city=city)
#     c.save()


# def download_from_vc(enddate=date.today()):
#     link = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?'
#     # VC_KEY = os.environ.get('VC_KEY')
#     try:
#         latest_saved = OneDayData.objects.latest('id').date
#     except ObjectDoesNotExist:
#             latest_saved = date(2010, 1, 1)
#
#     if latest_saved == enddate:
#         return
#     elif latest_saved == date(2010, 1, 1):
#         startdate = latest_saved
#     else:
#         startdate = latest_saved + timedelta(1)
#
#     def downloader(startdate, enddate):
#         for obj in CityList.objects.all():
#             print(type(obj))
#             city = str(obj)
#             payload = {
#                 "locations": city,
#                 "aggregateHours": '24',
#                 'unitGroup': 'metric',
#                 "startDateTime": startdate,
#                 "endDateTime": enddate,
#                 "contentType": "json",
#                 "key": VC_KEY,
#             }
#             response = requests.get(link, params=payload)
#             print(response.json())
#             for day in response.json()['locations'][city]['values']:
#                 o = OneDayData(
#                     city=obj,
#                     date=day['datetimeStr'][:10],
#                     maxTemp=day['maxt'],
#                     minTemp=day['mint'],
#                     avgTemp=day['temp'],
#                     windSpeed=round(day['wspd'] / 3.6),
#                     windDir=day['wdir'],
#                     precipitation=day['precip'],
#                     desc=day['conditions']
#                 )
#                 o.save()
#
#     if (enddate - startdate).days <= 10:
#         return downloader(startdate, enddate)
#     elif (enddate - startdate).days > 10:
#         while startdate < (enddate - timedelta(10)):
#             downloader(startdate, startdate + timedelta(10))
#             startdate += timedelta(10)
#         downloader(startdate, enddate)


def download_from_wwo(enddate=date.today()):
    """checks db and gets updates from api"""
    link = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
    # wwo_api_key = os.environ.get('WWO_API')

    try:
        latest_saved = OneDayData.objects.latest('id').date
    except ObjectDoesNotExist:
        latest_saved = date(2010, 1, 1)

    if latest_saved == enddate:
        return
    elif latest_saved == date(2010, 1, 1):
        startdate = latest_saved
    else:
        startdate = latest_saved + timedelta(1)

    def downloader(startdate, enddate):
        for obj in CityList.objects.all():
            city = str(obj)
            payload = {
                "q": city,
                "tp": '24',
                "date": startdate,
                "enddate": enddate,
                "format": "json",
                "key": wwo_api_key
            }
            response = requests.get(link, params=payload)

            try:  # in case of empty response at start of the day
                weather = response.json()['data']['weather']
            except KeyError:
                return

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

    # api provides only 35 days data in one request
    if (enddate - startdate).days <= 35:
        return downloader(startdate, enddate)
    elif (enddate - startdate).days > 35:
        while startdate < (enddate - timedelta(35)):
            downloader(startdate, enddate)
            startdate += timedelta(35)
        downloader(startdate, enddate)
