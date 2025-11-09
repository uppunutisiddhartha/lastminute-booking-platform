"""
URL configuration for Lastminuteai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.rolelogin, name='rolelogin'),
    path('logout/', views.logout_view, name='logout'),
    path('customer_register/', views.customer_register, name='customer_register'),
    path('hotel_booking/<int:hotel_id>/', views.hotel_booking, name='hotel_booking'),

    # ✅ Move these BEFORE hotel_detail
    path('hotel/<int:hotel_id>/payment/', views.payment, name='payment'),
    path('hotel/<int:hotel_id>/confirm_checkin/', views.confirm_checkin_hotel, name='confirm_checkin_hotel'),
    path('booking_conformed/<int:hotel_id>/', views.booking_conformed, name='booking_conformed'),

    # Keep this AFTER all specific hotel routes
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),

    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("search_flights/", views.search_flights, name="search_flights"),
    path('flight_checkout', views.flight_checkout, name="flight_checkout"),
    path("confirm-payment/", views.confirm_payment, name="confirm_payment"),
    path('support', views.support, name="support"),
]


