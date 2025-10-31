from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import datetime
from django.shortcuts import get_object_or_404



# Dealer Registration
def dealer_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        state = request.POST.get('state')
        city = request.POST.get('city')
        name_of_company = request.POST.get('name_of_company')

        if password != confirm_password:
            return render(request, 'auths/dealer_register.html', {'error': "Passwords do not match"})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'auths/dealer_register.html', {'error': "Username already exists"})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'auths/dealer_register.html', {'error': "Email already exists"})

        user = CustomUser.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            phone=phone,
            name=name,
            state=state,
            city=city,
            role='dealer',
        )

        Dealer.objects.create(user=user, name_of_company=name_of_company)

        login(request, user)
        return redirect('rolelogin')  

    return render(request, 'auths/dealer_register.html')

@login_required
def add_hotel(request):
    dealer = Dealer.objects.get(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description')
        Image = request.FILES.get('Hotel_image')  # Use FILES for image uploads!

        try:
            floor_count = int(request.POST.get('floor_count', 1))
            rooms_per_floor = int(request.POST.get('rooms_per_floor', 1))
            start_number = int(request.POST.get('start_number', 101))
        except ValueError:
            return render(request, 'add_hotel.html', {
                'error': "Floors, rooms per floor, and start number must be integers."
            })

        if not name or not location:
            return render(request, 'add_hotel.html', {
                'error': "Hotel name and location are required."
            })

        # ✅ Create the hotel
        hotel = Hotel.objects.create(
            dealer=dealer,
            name=name,
            location=location,
            description=description,
            floor_count=floor_count,
            Hotel_image=Image
        )

        # ✅ Generate rooms automatically
        for floor in range(1, floor_count + 1):
            for i in range(rooms_per_floor):
                room_no = start_number + (floor - 1) * 100 + i
                HotelRoom.objects.create(
                    #dealer=dealer,
                    hotel=hotel,
                    floor_number=floor,
                    room_number=str(room_no),
                    room_type='Standard',  # default room type if needed
                    price_per_night=1000,  # default price if model requires
                    capacity=2,            # default capacity
                    available=True
                )

        messages.success(request, f"Hotel '{hotel.name}' created with {floor_count} floors and {rooms_per_floor} rooms per floor.")
        return redirect('manage_rooms', hotel_id=hotel.id)

    return render(request, 'add_hotel.html')


@login_required
def dealer_dashboard(request):
    dealer = Dealer.objects.get(user=request.user)
    hotels = dealer.hotels.all()
    #flights = dealer.flights.all()

    # Fetch all bookings for rooms in dealer's hotels
    bookings = Booking.objects.filter(hotel_room__hotel__in=hotels).order_by("-check_in")

    return render(request, 'dealer_dashboard.html', {
        'hotels': hotels,
        #'flights': flights,
        'bookings': bookings,  # pass bookings to template
    })



#add hotel Room@login_required
@login_required
def add_room(request, hotel_id, room_id=None):
    hotel = get_object_or_404(Hotel, id=hotel_id, dealer__user=request.user)
    room = None  # Default: no room, will be used for "Add Room"

    # If room_id is passed, we are editing
    if room_id:
        room = get_object_or_404(HotelRoom, id=room_id, hotel=hotel)

    if request.method == 'POST':
        floor_number = request.POST.get('floor_number')
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        price_per_night = request.POST.get('price_per_night')
        capacity = request.POST.get('capacity')
        available = request.POST.get('available') == 'on'

        if not all([floor_number, room_number, room_type, price_per_night, capacity]):
            return render(
                request, 
                'add_room.html', 
                {'error': 'All fields are required.', 'hotel': hotel, 'room': room}
            )

        # Edit existing room
        if room:
            room.floor_number = int(floor_number)
            room.room_number = room_number
            room.room_type = room_type
            room.price_per_night = price_per_night
            room.capacity = int(capacity)
            room.available = available
            room.save()
            messages.success(request, f"Room {room.room_number} updated successfully.")
        else:
            # Create new room
            HotelRoom.objects.create(
                hotel=hotel,
                floor_number=int(floor_number),
                room_number=room_number,
                room_type=room_type,
                price_per_night=price_per_night,
                capacity=int(capacity),
                available=True
            )
            messages.success(request, f"Room {room_number} added successfully.")

        return redirect('manage_rooms', hotel_id=hotel.id)

    return render(request, 'add_room.html', {'hotel': hotel, 'room': room})

"""
@login_required
def add_hotel(request):
    if request.method == 'POST':
        dealer = Dealer.objects.get(user=request.user)
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description')

        if name and location:
            Hotel.objects.create(
                dealer=dealer,
                name=name,
                location=location,
                description=description
            )
            return redirect('add_hotel')
        else:
            return render(request, 'dashboard/add_hotel.html', {'error': 'All fields are required.'})

    return render(request, 'add_hotel.html')
"""

@login_required
def manage_rooms(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, dealer__user=request.user)
    rooms = hotel.rooms.all()  # All rooms for this hotel
    # Room statistics
    total_rooms = rooms.count()
    booked_rooms = rooms.filter(available=False).count()
    ready_rooms = rooms.filter(available=True).count()

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'total_rooms': total_rooms,
        'booked_rooms': booked_rooms,
        'ready_rooms': ready_rooms,
    }

    return render(request, 'manage_rooms.html', context)




@login_required
def edit_room(request, room_id):
    room = get_object_or_404(HotelRoom, id=room_id)

    if request.method == "POST":
        room.floor_number = int(request.POST.get('floor_number'))
        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.price_per_night = float(request.POST.get('price_per_night'))
        room.capacity = int(request.POST.get('capacity'))
        room.available = request.POST.get('available') == 'on'
        room.save()
        messages.success(request, f"Room {room.room_number} updated successfully.")
        return redirect('manage_rooms', hotel_id=room.hotel.id)

    return render(request, 'edit_room.html', {'room': room})




def bookings(request):
    if request.user.role != 'dealer':
         messages.error(request, "Access denied. Only dealers can view bookings.")
         return redirect('rolelogin')
    # dealer_rooms = HotelRoom.objects.filter(hotel__dealer=request.user)
    dealer = Dealer.objects.get(user=request.user)
    # Get all bookings for those rooms
    dealer_rooms = HotelRoom.objects.filter(hotel__dealer=dealer)
    bookings = Booking.objects.filter(hotel_room__in=dealer_rooms).select_related('hotel_room', 'user')

    context = {
        'bookings': bookings
    }
    return render(request, "booking.html",context)

