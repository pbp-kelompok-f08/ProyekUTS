from django import forms
from django.core.exceptions import ValidationError
from .models import Booking
from datetime import datetime


class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            # Check if the booking is in the past
            now = datetime.now().date()
            if date < now:
                raise ValidationError("Cannot book venues in the past.")

        return cleaned_data