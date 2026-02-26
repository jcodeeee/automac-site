from django.urls import path
from . import views

urlpatterns = [
    # customer
    path("", views.home, name="home"),
    path("inventory/", views.inventory, name="inventory"),
    path("cars/<int:pk>/", views.car_detail, name="car_detail"),
    path("cars/<int:pk>/book/", views.book_test_drive, name="book_test_drive"),

    # auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # owner
    path("owner/", views.owner_dashboard, name="owner_dashboard"),
    path("owner/cars/add/", views.car_create, name="car_create"),
    path("owner/cars/<int:pk>/edit/", views.car_edit, name="car_edit"),
    path("owner/cars/<int:pk>/sold/", views.car_mark_sold, name="car_mark_sold"),
    path("owner/cars/<int:pk>/available/", views.car_mark_available, name="car_mark_available"),

    # image management
    path("owner/cars/<int:pk>/images/", views.car_manage_images, name="car_manage_images"),
    path("owner/cars/<int:pk>/images/<int:img_id>/main/", views.car_set_main_image, name="car_set_main_image"),
    path("owner/cars/<int:pk>/images/<int:img_id>/delete/", views.car_delete_image, name="car_delete_image"),

    # booking status
    path("owner/bookings/<int:booking_id>/<str:status>/", views.booking_update_status, name="booking_update_status"),
    path("owner/bookings/<int:booking_id>/delete/", views.booking_delete, name="booking_delete"),
]
