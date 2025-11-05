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
    dealer=request.user.dealer
    exixting_hotels=Hotel.objects.filter(dealer=dealer)
    
    if exixting_hotels.count()>=5:
        messages.error(request, "You have reached the maximum limit of hotels you can add.")
        return redirect('dealer_dashboard')
    
    if request.method == 'POST':
        dealer_id = request.POST.get('dealer_id')
        dealer = Dealer.objects.get(id=dealer_id)
        
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description')
        floor_count = request.POST.get('floor_count') or 1
        hotel_image = request.FILES.get('hotel_image')
        ac_room_count = request.POST.get('ac_room_count') or 0
        non_ac_room_count = request.POST.get('non_ac_room_count') or 0

        # Boolean fields (checkboxes)
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

        # Optional: extra amenities from text input (comma-separated)
        extras = request.POST.get('extra_amenities')
        extra_amenities = [item.strip() for item in extras.split(',')] if extras else []

        # Create Hotel object
        Hotel.objects.create(
            dealer=dealer,
            name=name,
            location=location,
            description=description,
            floor_count=floor_count,
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

        messages.success(request, 'Hotel added successfully!')
        return redirect('add_hotel')  # change this to your list page name

    dealers = Dealer.objects.all()
    return render(request, 'add_hotel.html', {'dealers': dealers})






@login_required
def dealer_dashboard(request):
    dealer = Dealer.objects.get(user=request.user)
    hotels = dealer.hotels.all()
    
    #Booking.objects.filter(hotel=hotels)


    return render(request, 'dealer_dashboard.html', {
        'hotels': hotels,
        
        'bookings': bookings,  
    })

def bookings(request):
    if request.user.role != 'dealer':
         messages.error(request, "Access denied. Only dealers can view bookings.")
         return redirect('rolelogin')
    # dealer_rooms = HotelRoom.objects.filter(hotel__dealer=request.user)
    dealer = Dealer.objects.get(user=request.user)
    # Get all bookings for those rooms
    dealer_rooms = Hotel.objects.filter(hotel__dealer=dealer)
    bookings = Booking.objects.filter(hotel_room__in=dealer_rooms).select_related('hotel_room', 'user')

    context = {
        'bookings': bookings
    }
    return render(request, "booking.html",context)









































































































































































































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

