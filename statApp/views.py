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
            city = post_date['city']
            start_date = post_date['start_date']
            end_date = post_date['end_date']

            raw_data = OneDayData.objects.filter(
                city=city,
                date__range=[start_date, end_date]
            )

            # .aggregate(
            #     day_count=Count('date'),
            #     abs_min_temp=Min('minTemp'),
            #     avg_temp=Avg('avgTemp'),
            #     abs_max_temp=Max('maxTemp'),
            #     precip_days=Count('precipitation', filter=Q(precipitation=0)),
            #     avg_wind_speed=Avg('windSpeed'),
            # )
            stat = {}

            stat['city'] = city
            stat['start_date'] = raw_data.first().date
            stat['end_date'] = raw_data.last().date
            stat['day_count'] = raw_data.aggregate(Count('date'))

            stat['abs_min_temp'] = raw_data.aggregate(Min('minTemp'))['minTemp__min']
            stat['avg_temp'] = raw_data.aggregate(Avg('avgTemp'))['avgTemp__avg']
            stat['abs_max_temp'] = raw_data.aggregate(Max('maxTemp'))['maxTemp__max']

            if int(start_date[:4]) < int(end_date[:4]) + 2:
                stat['year_min'] = raw_data.values('date__year').annotate(
                    Avg('minTemp')
                ).order_by("date__year")[0]['minTemp__avg']

                stat['year_max'] = raw_data.values('date__year').annotate(
                    Avg('maxTemp')
                ).order_by('date__year')[0]['maxTemp__avg']

            stat['same_temp_day'] =

            days_zero_prec = raw_data.annotate(Count('precipitation')).filter(precipitation=0).count()
            stat['precip_days'] = round(days_zero_prec / raw_data.annotate(ays=Count('precipitation')).count() * 100)

            desc_list = [x['desc'] for x in raw_data.values('desc').annotate(count=Count('desc')).order_by('-count')[:2]]
            stat['most_frequent_prec'] = ', '.join(desc_list)

            stat['avg_wind_speed'] = raw_data.aggregate(Avg('windSpeed'))['windSpeed__avg']

            stat['avg_wind_dir'] = raw_data.aggregate(Avg('windDir'))['windDir__avg']

            context['stat'] = stat

            print('stat: ', stat['abs_min_temp'], stat['precip_days'])

        return context

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
