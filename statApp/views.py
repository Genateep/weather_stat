import urllib.request
from urllib.error import HTTPError
import json
from .models import OneDayData
from .forms import *
from django.views.generic import TemplateView
from django.db.models import Min, Max, Avg, Count
from django.shortcuts import render
from .downloader import *


class IndexPage(TemplateView):

    template_name = 'statApp/form_get_weather.html'
    city_and_date_class = CityAndDatesForm

    def post(self, request):
        post_data = request.POST or None
        context = self.get_context_data(
            request=request,
            city_and_date_form=CityAndDatesForm(post_data)
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        if 'city_and_date_form' not in kwargs:
            kwargs['city_and_date_form'] = CityAndDatesForm()
        context = super(IndexPage, self).get_context_data(**kwargs)

        print('kwargs: ', kwargs['request'].POST)

        post_date = kwargs['request'].POST or None

        if post_date:

            download_from_wwo()

            city = post_date['city']
            start_date = post_date['start_date']
            end_date = post_date['end_date']

            if start_date > end_date:  # to prevent invalid data input
                return context

            raw_data = OneDayData.objects.filter(
                city=city,
                date__range=[start_date, end_date]
            )
            if not raw_data:  # in case of empty response at start of the day
                return context

            stat = dict()
            stat['city'] = city
            stat['start_date'] = raw_data.first().date
            stat['end_date'] = raw_data.last().date
            stat['day_count'] = raw_data.aggregate(Count('date'))

            stat['abs_min_temp'] = raw_data.aggregate(Min('minTemp'))['minTemp__min']
            stat['avg_temp'] = round(raw_data.aggregate(Avg('avgTemp'))['avgTemp__avg'], 1)
            stat['abs_max_temp'] = raw_data.aggregate(Max('maxTemp'))['maxTemp__max']

            if int(start_date[:4]) < int(end_date[:4]) + 2:
                stat['year_min'] = round(raw_data.values('date__year').annotate(
                    Avg('minTemp')
                ).order_by("date__year")[0]['minTemp__avg'], 1)

                stat['year_max'] = round(raw_data.values('date__year').annotate(
                    Avg('maxTemp')
                ).order_by('date__year')[0]['maxTemp__avg'], 1)

            # stat['same_temp_day'] = ...

            days_zero_prec = raw_data.annotate(
                Count('precipitation')
            ).filter(precipitation=0).count()
            stat['precip_days'] = round(
                days_zero_prec / raw_data.annotate(Count('precipitation')).count() * 100
            )

            pr_count = raw_data.values('desc').annotate(count=Count('desc')).order_by('-count')[:2]
            desc_list = [x['desc'] for x in pr_count]
            stat['most_frequent_prec'] = ', '.join(desc_list)

            stat['avg_wind_speed'] = round(raw_data.aggregate(Avg('windSpeed'))['windSpeed__avg'], 1)

            # stat['avg_wind_dir'] = round(raw_data.aggregate(Avg('windDir'))['windDir__avg'])
            stat['avg_wind_dir'] = raw_data.values('windDir').annotate(count=Count('windDir')).order_by('-count')[0]['windDir']

            context['stat'] = stat

        return context

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
