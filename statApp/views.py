from django.shortcuts import render

import urllib.request
from urllib.error import HTTPError
import json
from .models import OneDayData


def index(request):
    data = {}
    if request.method == 'POST':
        try:
            city = request.POST['city']
            source = urllib.request.urlopen(
                'http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&appid=9ab890ef5f3c2b0fb1bb0fdac24d8f17'  # noqa
            ).read()
            list_of_data = json.loads(source)

            data = {
                'temp_min': str(list_of_data['main']['temp_min']),
                'temp_max': str(list_of_data['main']['temp_max']),
                'wind_speed': str(list_of_data['wind']['speed']),
                'wind_deg': str(list_of_data['wind']['deg']),
                'description': list_of_data['weather'][0]['description'],
                'icon': list_of_data['weather'][0]['icon'],
            }
            print(data)
        except HTTPError as err:
            if err.code == 404:
                data = {}

    return render(request, 'main/index.html', data)
