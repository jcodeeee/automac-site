from django import forms
from .models import Car, Booking

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "brand","model","year","price","mileage",
            "transmission","fuel","location","description","is_available"
        ]

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultiImageForm(forms.Form):
    images = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={"multiple": True})
    )

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["full_name","phone","email","preferred_date","preferred_time","note"]