from django.shortcuts import render

import urllib.request
from urllib.error import HTTPError
import json
from .models import OneDayData
from .forms import *
from django.views.generic import TemplateView
from django.db.models import Q, Min, Max, Avg, Count
from django.db.models.functions import Coalesce
# from django.utils.functional import cached_property


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
            stat = OneDayData.objects.filter(
                city=post_date['city'],
                date__range=[post_date['start_date'], post_date['end_date']]
            ).aggregate(
                day_count=Count('date'),
                abs_min_temp=Min('minTemp'),
                avg_temp=Avg('avgTemp'),
                abs_max_temp=Max('maxTemp'),
                precip_days=Count('precipitation', filter=Q(precipitation=0)),
                description='desc',
                avg_wind_speed=Avg('windSpeed'),
                wind_dir='windDir'
            )

            # calculating % of precip days
            stat['precip_days'] = str(round(stat['precip_days'] / stat['day_count'] * 100)) + ' %'

            context['stat'] = stat

            print('stat: ', stat['abs_min_temp'], stat['precip_days'])

        return context

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
