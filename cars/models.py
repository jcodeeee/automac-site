from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    brand = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    mileage = models.IntegerField(default=0)
    transmission = models.CharField(max_length=20, default="Automatic")
    fuel = models.CharField(max_length=20, default="Gasoline")
    location = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    main_image = models.ForeignKey(
        "CarImage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_for"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.year} {self.brand} {self.model}"

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="cars/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.car}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Done", "Done"),
    ]
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="bookings")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.car} ({self.status})"
