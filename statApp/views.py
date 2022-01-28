from django.views.generic import TemplateView

from .forms import CityAndDatesForm
from .instr.calculator import Calculator
from .models import OneDayData
from time import time


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
            post_time = time()
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

            context['stat'] = Calculator(  # creates calculated parameters
                raw_data,
                city,
                start_date,
                end_date,
                post_time
            ).stat
        return context

    def get(self, request, *args, **kwargs):
        return self.post(request)
