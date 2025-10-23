from django.urls import path
from . import views

app_name = "booking_venue"

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('book/<uuid:venue_id>/', views.book_venue, name='book_venue'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
