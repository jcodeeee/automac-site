from django import forms
from datetime import date
from decimal import Decimal, InvalidOperation
from .models import Car, Booking

class CarForm(forms.ModelForm):
    BRAND_CHOICES = [
        "Toyota", "Mitsubishi", "Honda", "Nissan", "Suzuki", "Ford", "Isuzu", "Hyundai",
        "Kia", "Mazda", "Chevrolet", "Subaru", "Volkswagen", "BMW", "Mercedes-Benz",
        "Audi", "Lexus", "Porsche", "Jeep", "Tesla", "MG", "BYD", "Chery", "Geely",
    ]
    MODEL_CHOICES = [
        "Vios", "Yaris", "Corolla Altis", "Camry", "Innova", "Fortuner", "Hilux", "Rush", "Wigo",
        "Montero Sport", "Strada", "Mirage", "Xpander", "L300", "Adventure",
        "Civic", "City", "Brio", "HR-V", "CR-V", "Jazz", "Mobilio",
        "Almera", "Navara", "Terra", "Juke", "Patrol", "Urvan",
        "Swift", "Dzire", "Ertiga", "Celerio", "Jimny", "APV", "Carry",
        "Everest", "Ranger", "Territory", "Explorer",
        "D-Max", "MU-X",
        "Accent", "Elantra", "Tucson", "Santa Fe", "Stargazer",
        "Picanto", "Rio", "Seltos", "Sportage",
        "Mazda2", "Mazda3", "CX-3", "CX-5", "CX-9",
        "Model 3", "Model Y",
    ]
    TRANSMISSION_CHOICES = ["Automatic", "Manual", "CVT", "DCT", "AT", "MT"]
    FUEL_CHOICES = ["Gasoline", "Diesel", "Hybrid", "Electric", "LPG"]

    class Meta:
        model = Car
        fields = [
            "brand","model","year","price","mileage",
            "transmission","fuel","description","is_available"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        year_choices = [(y, str(y)) for y in range(current_year, 1989, -1)]

        brand_choices = [("", "Select brand")] + [(b, b) for b in self.BRAND_CHOICES]
        model_choices = [("", "Select model")] + [(m, m) for m in self.MODEL_CHOICES]
        trans_choices = [("", "Select transmission")] + [(t, t) for t in self.TRANSMISSION_CHOICES]
        fuel_choices = [("", "Select fuel")] + [(f, f) for f in self.FUEL_CHOICES]

        if self.instance and self.instance.pk:
            if self.instance.brand and self.instance.brand not in self.BRAND_CHOICES:
                brand_choices.append((self.instance.brand, self.instance.brand))
            if self.instance.model and self.instance.model not in self.MODEL_CHOICES:
                model_choices.append((self.instance.model, self.instance.model))
            if self.instance.transmission and self.instance.transmission not in self.TRANSMISSION_CHOICES:
                trans_choices.append((self.instance.transmission, self.instance.transmission))
            if self.instance.fuel and self.instance.fuel not in self.FUEL_CHOICES:
                fuel_choices.append((self.instance.fuel, self.instance.fuel))

        self.fields["brand"] = forms.ChoiceField(choices=brand_choices, required=True)
        self.fields["model"] = forms.ChoiceField(choices=model_choices, required=True)
        self.fields["year"] = forms.TypedChoiceField(
            choices=[("", "Select year")] + year_choices,
            coerce=int,
            required=True,
        )
        self.fields["transmission"] = forms.ChoiceField(choices=trans_choices, required=True)
        self.fields["fuel"] = forms.ChoiceField(choices=fuel_choices, required=True)

        self.fields["price"].widget.attrs.update({"placeholder": "e.g. 1,250,000"})

        for name, field in self.fields.items():
            if name == "is_available":
                field.widget.attrs.update({"class": "form-check-input"})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select soft-input"})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-control soft-input", "rows": "4"})
            else:
                field.widget.attrs.update({"class": "form-control soft-input"})

    def clean_price(self):
        raw = str(self.cleaned_data.get("price", "")).replace(",", "")
        try:
            return Decimal(raw)
        except (TypeError, ValueError, InvalidOperation):
            raise forms.ValidationError("Enter a valid price.")

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
