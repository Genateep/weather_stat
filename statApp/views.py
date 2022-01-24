from django.db.models import Avg, Count, Max, Min
from django.views.generic import TemplateView

from .downloader import download_from_wwo
from .forms import CityAndDatesForm
from .models import OneDayData


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
        post_data = kwargs['request'].POST or None

        if post_data:
            download_from_wwo()

            city = post_data['city']
            start_date = post_data['start_date']
            end_date = post_data['end_date']

            if start_date > end_date:
                return context  # to prevent errors by invalid date input

            raw_data = OneDayData.objects.filter(
                city=city,
                date__range=[start_date, end_date]
            )

            if not raw_data:  # in case of empty suite e.g. at start of the day
                return context

            stat = dict()
            stat['city'] = city
            stat['start_date'] = raw_data.first().date
            stat['end_date'] = raw_data.last().date
            stat['day_count'] = raw_data.aggregate(Count('date'))

            stat['abs_min_temp'] = raw_data.aggregate(Min('minTemp'))['minTemp__min']  # noqa
            stat['avg_temp'] = round(raw_data.aggregate(Avg('avgTemp'))['avgTemp__avg'], 1)  # noqa
            stat['abs_max_temp'] = raw_data.aggregate(Max('maxTemp'))['maxTemp__max']  # noqa

            # calculates year averages of full years if search period > 2 years
            if int(start_date[:4]) <= int(end_date[:4]) - 2:
                year_min_avg = list(raw_data.values('date__year').annotate(  # noqa
                    Avg('minTemp')
                ).order_by("date__year"))
                stat['year_min'] = year_min_avg[1:-1]
                for x in stat['year_min']:
                    x['minTemp__avg'] = round(x['minTemp__avg'], 1)

                year_max_avg = list(raw_data.values('date__year').annotate(  # noqa
                    Avg('maxTemp')
                ).order_by("date__year"))
                stat['year_max'] = year_max_avg[1:-1]
                for x in stat['year_max']:
                    x['maxTemp__avg'] = round(x['maxTemp__avg'], 1)

            # stat['same_temp_day'] = ...

            # calculates percentage of days with precipitation
            days_zero_prec = raw_data.annotate(
                Count('precipitation')
            ).filter(precipitation=0).count()
            stat['precip_days'] = round(
                days_zero_prec / raw_data.annotate(Count('precipitation')).count() * 100  # noqa
            )

            # calculates two most frequent precipitation descriptions
            pr_count = raw_data.values('desc').annotate(count=Count('desc')).filter(precipitation__gt=0).order_by('-count')[:2]  # noqa
            stat['most_frequent_prec'] = ', '.join(x['desc'] for x in pr_count)  # noqa

            stat['avg_wind_speed'] = round(raw_data.aggregate(Avg('windSpeed'))['windSpeed__avg'], 1)  # noqa

            # first option for degree fields second for most frequent
            # stat['avg_wind_dir'] = round(raw_data.aggregate(Avg('windDir'))['windDir__avg'])  # noqa
            stat['avg_wind_dir'] = raw_data.values('windDir').annotate(count=Count('windDir')).order_by('-count')[0]['windDir']  # noqa

            context['stat'] = stat

        return context

    def get(self, request, *args, **kwargs):
        return self.post(request)
