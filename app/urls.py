"""
URL configuration for Lastminuteai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('login/', views.rolelogin, name='rolelogin'),
    path('logout/', views.logout_view, name='logout'),
    path('customer_register/', views.customer_register, name='customer_register'),
   # path('flight_booking/', views.flight_booking, name='flight_booking'),
    path('hotel_booking/', views.hotel_booking, name='hotel_booking'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("book-room/<int:room_id>/", views.book_room, name="book_room"),

     path("search_flights/", views.search_flights, name="search_flights"),
    #path("results/<str:source>/<str:destination>/", views.flight_results, name="flight_results"),
   # path("book/<int:flight_id>/", views.book_flight, name="book_flight"),
   #path("book-api/", views.book_flight_api, name="book_flight_api"),
   path('flight_checkout',views.flight_checkout,name="flight_checkout"),
path("confirm-payment/", views.confirm_payment, name="confirm_payment"),



]

