from django.shortcuts import render

import urllib.request
from urllib.error import HTTPError
import json
from .models import OneDayData
from .forms import *
from django.views.generic import TemplateView
from django.db.models import Q, Min, Max, Avg, Count
from django.db.models.functions import Coalesce


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


class IndexPage(TemplateView):

    template_name = 'statApp/form_get_weather.html'
    city_and_date_class = CityAndDatesForm

    def post(self, request):
        post_data = request.POST or None
        # city_and_date_form = self.city_and_date_class(post_data)
        # city_and_date_form = CityAndDatesForm(post_data)

        # context = self.get_context_data(request=request, city_and_date_form=city_and_date_form)
        context = self.get_context_data(request=request, city_and_date_form=CityAndDatesForm(post_data))

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        if 'city_and_date_form' not in kwargs:
            kwargs['city_and_date_form'] = CityAndDatesForm()
        context = super(IndexPage, self).get_context_data(**kwargs)

        print('kwargs: ', kwargs['request'].POST)

        post_date = kwargs['request'].POST or None

        if post_date:
            # делаем запрос в бд по фильтру и получаем среднее значение
            # abs_min_temp = Coalesce(Min('minTemp'), 0)
            stat_weather = OneDayData.objects.filter(
                city=post_date['city'],
                date__range=[post_date['start_date'], post_date['end_date']]
            ).aggregate(
                abs_min_temp=Min('minTemp'),
                avg_temp=Avg('avgTemp'),
                abs_max_temp=Max('maxTemp'),
                precip_days=Count('precipitation', filter=Q(precipitation=0))
            )
            print('stat_weather: ', stat_weather['abs_min_temp'])

            context['stat_weather'] = stat_weather

        return context

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
