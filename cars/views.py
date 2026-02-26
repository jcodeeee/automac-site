from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Min, Max, Count, Sum
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from django.utils import timezone

from .models import Car, CarImage, Booking
from .forms import CarForm, MultiImageForm, BookingForm

# ---------- AUTH ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("owner_dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("owner_dashboard")
    return render(request, "cars/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")

# ---------- CUSTOMER ----------
def home(request):
    latest = Car.objects.filter(is_available=True).order_by("-created_at")[:6]
    return render(request, "cars/home.html", {"latest": latest})

def inventory(request):
    qs = Car.objects.filter(is_available=True)

    q = request.GET.get("q","").strip()
    brand = request.GET.get("brand","").strip()
    trans = request.GET.get("trans","").strip()
    fuel = request.GET.get("fuel","").strip()
    min_price_raw = request.GET.get("min_price","").strip()
    max_price_raw = request.GET.get("max_price","").strip()
    min_price = min_price_raw.replace(",", "")
    max_price = max_price_raw.replace(",", "")
    min_year = request.GET.get("min_year","").strip()
    max_year = request.GET.get("max_year","").strip()
    sort = request.GET.get("sort", "newest").strip()

    if q:
        qs = qs.filter(
            Q(brand__icontains=q) |
            Q(model__icontains=q) |
            Q(location__icontains=q) |
            Q(description__icontains=q)
        )
    if brand:
        qs = qs.filter(brand__iexact=brand)
    if trans:
        qs = qs.filter(transmission__iexact=trans)
    if fuel:
        qs = qs.filter(fuel__iexact=fuel)

    if min_price.isdigit():
        qs = qs.filter(price__gte=min_price)
    if max_price.isdigit():
        qs = qs.filter(price__lte=max_price)

    if min_year.isdigit():
        qs = qs.filter(year__gte=min_year)
    if max_year.isdigit():
        qs = qs.filter(year__lte=max_year)

    sort_map = {
        "newest": "-created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "year_desc": "-year",
    }
    if sort not in sort_map:
        sort = "newest"
    qs = qs.order_by(sort_map[sort])

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    brand_options = (
        Car.objects.filter(is_available=True)
        .values("brand")
        .annotate(count=Count("id"))
        .order_by("brand")
    )
    stats = Car.objects.filter(is_available=True).aggregate(
        min_price=Min("price"), max_price=Max("price"),
        min_year=Min("year"), max_year=Max("year")
    )
    current_year = date.today().year
    year_options = list(range(current_year, 1899, -1))

    display_min_price = f"{int(min_price):,}" if min_price.isdigit() else min_price_raw
    display_max_price = f"{int(max_price):,}" if max_price.isdigit() else max_price_raw

    return render(request, "cars/inventory.html", {
        "cars": page_obj.object_list,
        "page_obj": page_obj,
        "brand_options": brand_options,
        "stats": stats,
        "year_options": year_options,
        "selected_sort": sort,
        "query_string": query_string,
        "display_min_price": display_min_price,
        "display_max_price": display_max_price,
    })

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk, is_available=True)
    form = BookingForm()
    return render(request, "cars/detail.html", {"car": car, "form": form})

def _send_owner_booking_email(booking: Booking):
    subject = f"New Test Drive Booking - #{booking.id}"
    msg = (
        f"New booking received.\n\n"
        f"Car: {booking.car}\n"
        f"Name: {booking.full_name}\n"
        f"Phone: {booking.phone}\n"
        f"Email: {booking.email}\n"
        f"Date/Time: {booking.preferred_date} {booking.preferred_time}\n"
        f"Note: {booking.note}\n"
        f"Status: {booking.status}\n"
    )
    recipients = []
    owner_email = booking.car.owner.email
    if owner_email:
        recipients.append(owner_email)
    alert_email = getattr(settings, "BOOKING_ALERT_EMAIL", "")
    if alert_email and alert_email not in recipients:
        recipients.append(alert_email)
    if recipients:
        send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)

def _send_customer_booking_email(booking: Booking):
    if not booking.email:
        return
    subject = f"Booking Received - {booking.car}"
    msg = (
        f"Hi {booking.full_name},\n\n"
        f"Your test drive request has been received.\n\n"
        f"Car: {booking.car}\n"
        f"Preferred schedule: {booking.preferred_date} {booking.preferred_time}\n"
        f"Current status: {booking.status}\n\n"
        f"We will contact you soon to confirm.\n\n"
        f"Thank you,\n"
        f"AutoMac Lucena"
    )
    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [booking.email], fail_silently=True)

def _send_customer_status_email(booking: Booking):
    if not booking.email:
        return
    subject = f"Booking Status Update - {booking.car}"
    msg = (
        f"Hi {booking.full_name},\n\n"
        f"Your booking status is now: {booking.status}\n\n"
        f"Car: {booking.car}\n"
        f"Preferred schedule: {booking.preferred_date} {booking.preferred_time}\n\n"
        f"Thank you,\n"
        f"AutoMac Lucena"
    )
    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [booking.email], fail_silently=True)

def _send_booking_notifications(booking: Booking):
    _send_owner_booking_email(booking)
    _send_customer_booking_email(booking)

    # OPTIONAL SMS (Twilio) - only runs if credentials are present
    if getattr(settings, "TWILIO_ACCOUNT_SID", "") and getattr(settings, "TWILIO_AUTH_TOKEN", "") and getattr(settings, "TWILIO_FROM_NUMBER", ""):
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"AutoHub booking: {booking.full_name} for {booking.car} on {booking.preferred_date} {booking.preferred_time}.",
                from_=settings.TWILIO_FROM_NUMBER,
                to=booking.phone
            )
        except Exception:
            # Don't crash the site if SMS fails
            pass

def book_test_drive(request, pk):
    car = get_object_or_404(Car, pk=pk, is_available=True)
    if request.method != "POST":
        return redirect("car_detail", pk=pk)

    form = BookingForm(request.POST)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.car = car
        booking.save()
        _send_booking_notifications(booking)
        return redirect("car_detail", pk=pk)

    return render(request, "cars/detail.html", {"car": car, "form": form})

# ---------- OWNER ----------
@login_required
def owner_dashboard(request):
    cars = Car.objects.filter(owner=request.user).order_by("-created_at")
    bookings = Booking.objects.filter(car__owner=request.user).order_by("-created_at")[:10]
    now = timezone.now()
    analytics = cars.aggregate(
        total_cars=Count("id"),
        available_count=Count("id", filter=Q(is_available=True)),
        sold_count=Count("id", filter=Q(sold_at__isnull=False)),
        sold_revenue=Sum("price", filter=Q(sold_at__isnull=False)),
        available_value=Sum("price", filter=Q(is_available=True)),
    )
    analytics["sold_this_month"] = cars.filter(
        sold_at__isnull=False,
        sold_at__year=now.year,
        sold_at__month=now.month,
    ).count()
    return render(request, "cars/owner_dashboard.html", {"cars": cars, "bookings": bookings, "analytics": analytics})

@login_required
def car_create(request):
    car_form = CarForm(request.POST or None)
    img_form = MultiImageForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and car_form.is_valid():
        car = car_form.save(commit=False)
        car.owner = request.user
        if not car.location:
            car.location = "Lucena City, Quezon"
        car.save()

        images = request.FILES.getlist("images")
        for f in images:
            img = CarImage.objects.create(car=car, image=f)
            if car.main_image is None:
                car.main_image = img
                car.save(update_fields=["main_image"])

        return redirect("owner_dashboard")

    return render(request, "cars/car_form.html", {
        "car_form": car_form,
        "img_form": img_form,
        "title": "Add Car",
        "brand_model_map": CarForm.BRAND_MODEL_MAP,
    })

@login_required
def car_edit(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)

    car_form = CarForm(request.POST or None, instance=car)
    img_form = MultiImageForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and car_form.is_valid():
        car = car_form.save()
        if not car.location:
            car.location = "Lucena City, Quezon"
            car.save(update_fields=["location"])
        if car.is_available and car.sold_at is not None:
            car.sold_at = None
            car.save(update_fields=["sold_at"])

        images = request.FILES.getlist("images")
        for f in images:
            img = CarImage.objects.create(car=car, image=f)
            if car.main_image is None:
                car.main_image = img
                car.save(update_fields=["main_image"])

        return redirect("car_manage_images", pk=car.id)

    return render(request, "cars/car_form.html", {
        "car_form": car_form,
        "img_form": img_form,
        "title": "Edit Car",
        "brand_model_map": CarForm.BRAND_MODEL_MAP,
    })

@login_required
def car_mark_sold(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    if car.is_available:
        car.is_available = False
        car.sold_at = timezone.now()
        car.save(update_fields=["is_available", "sold_at"])
    return redirect("owner_dashboard")

@login_required
def car_mark_available(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    if not car.is_available:
        car.is_available = True
        car.sold_at = None
        car.save(update_fields=["is_available", "sold_at"])
    return redirect("owner_dashboard")

@login_required
def car_manage_images(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    return render(request, "cars/car_images.html", {"car": car})

@login_required
def car_set_main_image(request, pk, img_id):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    img = get_object_or_404(CarImage, pk=img_id, car=car)
    car.main_image = img
    car.save(update_fields=["main_image"])
    return redirect("car_manage_images", pk=pk)

@login_required
def car_delete_image(request, pk, img_id):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    img = get_object_or_404(CarImage, pk=img_id, car=car)

    was_main = (car.main_image_id == img.id)
    img.delete()

    if was_main:
        car.main_image = car.images.first()  # next image or None
        car.save(update_fields=["main_image"])

    return redirect("car_manage_images", pk=pk)

@login_required
def booking_update_status(request, booking_id, status):
    booking = get_object_or_404(Booking, pk=booking_id, car__owner=request.user)
    if status not in ["Approved", "Rejected", "Done", "Pending"]:
        return redirect("owner_dashboard")
    booking.status = status
    booking.save(update_fields=["status"])
    _send_customer_status_email(booking)
    return redirect("owner_dashboard")
