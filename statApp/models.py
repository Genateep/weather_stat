from django.db import models


class OneDayData(models.Model):
    date = models.DateField()
    maxTemp = models.SmallIntegerField()
    minTemp = models.SmallIntegerField()
    avgTemp = models.SmallIntegerField()
    windSpeed = models.SmallIntegerField()
    windDir = models.CharField(max_length=3)
    precipitation = models.DecimalField(max_digits=4, decimal_places=1)
    desc = models.CharField(max_length=40)

    def __str__(self):
        return self.date


def get_info_from_site():
    WWO_API = '469327e52a7d4df9b31102143222101'
    link = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
    secret_key = WWO_API

    payload = {
        "q": "Moscow",
        "tp": '24',
        "date": f"{year}-{month}-01",
        "enddate": f"{year}-{month + 1}-01",
        "format": "json",
        "key": secret_key
    }
    response = requests.get(link, params=payload)
    for day in response.json()['data']['weather']:
        data['days'].append(
            {
                'date': day['date'],
                'maxTemp': day['maxtempC'],
                'minTemp': day['mintempC'],
                'avgTemp': day['avgtempC'],
                'windSpeed': day['hourly'][0]['windspeedKmph'],
                'windDir': day['hourly'][0]['winddir16Point'],
                'precipitation': day['hourly'][0]['precipMM'],
                'desc': day['hourly'][0]['weatherDesc'][0]['value']
            }
        )
    data['days'].pop()

