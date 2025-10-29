from django.urls import path
from . import dealer_views


urlpatterns = [
    path('dealer_register/', dealer_views.dealer_register, name='dealer_register'),
    path('dealer_dashboard/', dealer_views.dealer_dashboard, name='dealer_dashboard'),
     path('add-hotel/', dealer_views.add_hotel, name='add_hotel'),
    #path('add-flight/', dealer_views.add_flight, name='add_flight'),
    path('manage-rooms/<int:hotel_id>/', dealer_views.manage_rooms, name='manage_rooms'),
    path('add-room/<int:hotel_id>/', dealer_views.add_room, name='add_room'),
    path('edit-room/<int:room_id>/', dealer_views.edit_room, name='edit_room'),
    path('bookings/',dealer_views.bookings,name="bookings")

]