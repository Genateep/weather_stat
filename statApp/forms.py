from django import forms

from .models import OneDayData


class CityAndDatesForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date'
            }
        )
    )
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(
            attrs={
                'type': 'date'
            }
        )
    )

    class Meta:
        model = OneDayData
        fields = ['city', 'start_date', 'end_date']
