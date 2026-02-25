from django.contrib import admin
from .models import Car, CarImage, Booking

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id","brand","model","year","price","is_available","owner")
    search_fields = ("brand","model","location")
    inlines = [CarImageInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id","car","full_name","phone","preferred_date","preferred_time","status","created_at")
    list_filter = ("status","preferred_date")