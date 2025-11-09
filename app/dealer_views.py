from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta


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

from .models import Hotel, Dealer, Room

@login_required
def add_hotel(request):
    # Get the logged-in dealer directly
    dealer = request.user.dealer

    # Limit: only 1 hotel per dealer
    existing_hotels = Hotel.objects.filter(dealer=dealer)
    if existing_hotels.count() >= 1:
        messages.error(request, "You have reached the maximum limit of hotels you can add.")
        return redirect('dealer_dashboard')

    if request.method == 'POST':
        price = request.POST.get('price')
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description')
        floor_count = int(request.POST.get('floor_count') or 1)
        hotel_image = request.FILES.get('hotel_image')
        ac_room_count = int(request.POST.get('ac_room_count') or 0)
        non_ac_room_count = int(request.POST.get('non_ac_room_count') or 0)

        # Boolean fields
        has_wifi = 'has_wifi' in request.POST
        has_parking = 'has_parking' in request.POST
        has_tv = 'has_tv' in request.POST
        has_restaurant = 'has_restaurant' in request.POST
        has_dining = 'has_dining' in request.POST
        has_elevator = 'has_elevator' in request.POST
        has_cctv = 'has_cctv' in request.POST
        has_room_service = 'has_room_service' in request.POST
        has_swimming_pool = 'has_swimming_pool' in request.POST
        has_gym = 'has_gym' in request.POST

        extras = request.POST.get('extra_amenities')
        extra_amenities = [item.strip() for item in extras.split(',')] if extras else []

        # Create hotel linked to the logged-in dealer
        hotel = Hotel.objects.create(
            dealer=dealer,
            name=name,
            location=location,
            description=description,
            floor_count=floor_count,
            price=price,
            hotel_image=hotel_image,
            has_wifi=has_wifi,
            has_parking=has_parking,
            has_tv=has_tv,
            has_restaurant=has_restaurant,
            has_dining=has_dining,
            has_elevator=has_elevator,
            has_cctv=has_cctv,
            has_room_service=has_room_service,
            has_swimming_pool=has_swimming_pool,
            has_gym=has_gym,
            extra_amenities=extra_amenities,
            ac_room_count=ac_room_count,
            non_ac_room_count=non_ac_room_count
        )

        # Auto-generate rooms
        for i in range(1, ac_room_count + 1):
            Room.objects.create(hotel=hotel, room_number=f"AC-{i}", room_type='AC')
        for i in range(1, non_ac_room_count + 1):
            Room.objects.create(hotel=hotel, room_number=f"NAC-{i}", room_type='NON_AC')

        messages.success(request, 'Hotel and rooms added successfully!')
        return redirect('add_hotel')

    return render(request, 'add_hotel.html')



@login_required
def dealer_dashboard(request):
    dealer = Dealer.objects.get(user=request.user)
    hotels = dealer.hotels.all()
    bookings = Booking.objects.filter(hotel__in=hotels)

    return render(request, 'dealer_dashboard.html', {
        'hotels': hotels,
        'bookings': bookings,
    })

@login_required
def bookings(request):
    dealer = request.user.dealer
    hotels = Hotel.objects.filter(dealer=dealer)
    bookings = Booking.objects.filter(hotel__in=hotels)
    return render(request, "booking.html", {"bookings": bookings})





@login_required
def room_list(request, hotel_id):

    hotel = get_object_or_404(Hotel, id=hotel_id)
    #print("DEBUG → Hotel ID:", hotel.id, "Name:", hotel.name, "Room count:", hotel.rooms.count())
    rooms = hotel.rooms.all()
    return render(request, 'room_list.html', {'hotel': hotel, 'rooms': rooms})




@login_required
def room_checkin(request, room_id):

    room = get_object_or_404(Room, id=room_id)
    context = {
        'room': room,
        'hotel': room.hotel,
    }
    return render(request, 'check_in.html', context)


@login_required
def confirm_checkin(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    hotel = room.hotel

    if request.method == 'POST':
        guest_name = request.POST.get('guest_name')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        number_persons = request.POST.get('num_persons')

        # Validate dates

        try:
            check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "❌ Invalid date format. Please use YYYY-MM-DD.")
            return redirect('room_checkin', room_id=room.id)

        # ✅ Create booking record
        Booking.objects.create(
            user=request.user,
            email=request.user.email,
             number=request.user.phone,
            hotel=hotel,
            room=room,
            name=guest_name,
            check_in=check_in,
            check_out=check_out, 
            num_persons=number_persons,
        )

        # ✅ Update room status
        room.is_booked = True
        room.save()

        messages.success(request, f"✅ Room {room.room_number} checked in for {guest_name}.")
        return redirect('room_list', hotel_id=hotel.id)

    return redirect('room_list', hotel_id=hotel.id)


@login_required
def check_out(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    hotel = room.hotel
    # Update room status
    room.is_booked = False
    room.save()

 
    Booking.objects.filter(room=room, check_out=timezone.now().date()).update(check_out=timezone.now().date())

    messages.success(request, f"✅ Room {room.room_number} has been checked out successfully.")
    return redirect('room_list', hotel_id=hotel.id)




























































































































































































"""
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


"""

