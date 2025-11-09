from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from datetime import datetime, date, time, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages 
from datetime import datetime
from django.utils import timezone
import requests
import random
import io
from decimal import Decimal
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4  #for the pdf pip install reportlab

def index(request):
    hotels = Hotel.objects.all().prefetch_related('rooms')  # load all hotels with their rooms efficiently
    return render(request, 'index.html', {'hotels': hotels})



# Customer Registration
def customer_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')

        if password != confirm_password:
            return render(request, 'auths/customer_register.html', {'error': "Passwords do not match"})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'auths/customer_register.html', {'error': "Username already exists"})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'auths/customer_register.html', {'error': "Email already exists"})

        user = CustomUser.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            phone=phone,
            name=name,
            state=state,
            city=city,
            role='customer',
        )

        Customer.objects.create(user=user, address=address)

        login(request, user)
        return redirect('rolelogin')  

    return render(request, 'auths/customer_register.html')


# Login view for both (same login page, redirect based on role)
def rolelogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'dealer':
                return redirect('dealer_dashboard')
            else:
                return redirect('index')
        else:
            return render(request, 'auths/login.html', {'error': 'Invalid username or password'})

    return render(request, 'auths/login.html')



# Logout view
def logout_view(request):
    logout(request)
    return redirect('rolelogin')



# Hotel Booking Views
@login_required(login_url='rolelogin')
def hotel_booking(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    # hotel.views += 1
    # hotel.save()
    return render(request, 'hotel_booking.html', {'hotel': hotel})




def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    #rooms = hotel.rooms.all()  # related_name='rooms' on Room model
    reviews = Review.objects.filter(hotel=hotel).select_related('user').order_by('-created_at')

    context = {
        "hotel": hotel,
        #"rooms": rooms,
        "reviews": reviews,
    }
    return render(request, "hotel_detail.html", context)






@login_required(login_url='rolelogin')
def my_bookings(request):
    if request.user.role !="customer":
        messages.error(request,'u are not able to render to this page')
        return redirect("rolelogin")
    bookings = Booking.objects.filter(user=request.user).select_related('hotel_room__hotel')
    return render(request, "my_bookings.html", {"bookings": bookings})


def flight_coustomer(source, destination):
    api_key = settings.AVIATIONSTACK_API_KEY
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": api_key,
        "dep_iata": source,
        "arr_iata": destination,
        "limit": 10,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        flights_raw = data.get("data", [])

        flights = []
        for f in flights_raw:
            flights.append({
                "airline": f.get("airline", {}).get("name", "Unknown"),
                "flight_no": f.get("flight", {}).get("iata", "N/A"),
                "dep_airport": f.get("departure", {}).get("airport", "N/A"),
                "dep_time": f.get("departure", {}).get("scheduled", "N/A"),
                "arr_airport": f.get("arrival", {}).get("airport", "N/A"),
                "arr_time": f.get("arrival", {}).get("scheduled", "N/A"),
                "status": f.get("flight_status", "Unknown").capitalize(),
                "price":  round(3000 + (hash(f.get('flight', {}).get('iata', '0')) % 5000)),  # Dummy price
            })

        return flights

    except requests.RequestException as e:
        print(f"❌ Error fetching flight data: {e}")
        return []



def search_flights(request):
   
    if request.method == "POST":
        source = request.POST.get("source", "").strip().upper()
        destination = request.POST.get("destination", "").strip().upper()

        if not source or not destination:
            messages.error(request, "Please enter both source and destination.")
            return render(request, "flights/flight_customer.html")

        flights = flight_coustomer(source, destination)

        context = {
            "source": source,
            "destination": destination,
            "flights": flights,
        }
        return render(request, "flights/result_flight.html", context)

    return render(request, "flights/flight_customer.html")


def flight_results(request, source, destination):
    
    flights = flight_coustomer(source, destination)
    context = {
        "source": source,
        "destination": destination,
        "flights": flights,
    }
    return render(request, "flights/result_flight.html", context)


# ----------- Flight Checkout Page -----------

@login_required(login_url='rolelogin')
def flight_checkout(request):

    if request.method == "POST":
        airline = request.POST.get("airline")
        flight_no = request.POST.get("flight_no")
        dep_airport = request.POST.get("dep_airport")
        arr_airport = request.POST.get("arr_airport")
        dep_time = request.POST.get("dep_time")
        arr_time = request.POST.get("arr_time")
        price = request.POST.get("price")

        context = {
            "airline": airline,
            "flight_no": flight_no,
            "dep_airport": dep_airport,
            "arr_airport": arr_airport,
            "dep_time": dep_time,
            "arr_time": arr_time,
            "price": price,
        }
        return render(request, "flights/flight_checkout.html", context)

    return redirect("search_flights")



@login_required(login_url='rolelogin')
def confirm_payment(request):
    """
    Save booking info, send PDF ticket, and show payment confirmation.
    """
    if request.method == "POST":
        airline = request.POST.get("airline")
        flight_no = request.POST.get("flight_no")
        dep_airport = request.POST.get("dep_airport")
        arr_airport = request.POST.get("arr_airport")
        dep_time = request.POST.get("dep_time")
        arr_time = request.POST.get("arr_time")
        price = request.POST.get("price")
        passengers = int(request.POST.get("passengers", 1))
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        payment_method = request.POST.get("payment_method", "Credit Card")

        # ✅ Generate random seat (e.g., 12A)
        seat_row = random.randint(1, 30)
        seat_letter = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
        seat_number = f"{seat_row}{seat_letter}"

        # ✅ Save booking in DB
        booking = Flight_Booking.objects.create(
            user=request.user,
            flight_name=airline,
            flight_no=flight_no,
            source=dep_airport,
            destination=arr_airport,
            departure_time=dep_time,
            arrival_time=arr_time,
            passengers=passengers,
            passenger_name=fullname,
            email=email,
            phone=phone,
            payment_method=payment_method,
            total_price=price,
            seat_number=seat_number,
            payment_status="Success",
        )

        # ✅ Generate PDF ticket
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        p.setTitle("Flight Ticket - SkyFinder")
        p.setFont("Helvetica-Bold", 18)
        p.drawString(200, height - 80, "✈ - E-Ticket")

        p.setFont("Helvetica", 12)
        y = height - 130
        ticket_data = [
            ("Booking ID", str(booking.id)),
            ("Passenger Name", fullname),
            ("Airline", airline),
            ("Flight No", flight_no),
            ("From", dep_airport),
            ("To", arr_airport),
            ("Departure", dep_time),
            ("Arrival", arr_time),
            ("Seat Number", seat_number),
            ("Passengers", str(passengers)),
            ("Payment Method", payment_method),
            ("Total Paid", f"₹{price}"),
        ]

        for label, value in ticket_data:
            p.drawString(80, y, f"{label}: {value}")
            y -= 25

        p.drawString(80, y - 10, "Thank you for flying with SkyFinder!")
        p.showPage()
        p.save()
        pdf_buffer.seek(0)

        # ✅ Send confirmation email with PDF
        subject = f"Your SkyFinder Booking Confirmation - {booking.flight_no}"
        body = (
            f"Dear {fullname},\n\n"
            f"Your booking with SkyFinder is confirmed!\n"
            f"Flight: {airline} ({flight_no})\n"
            f"From: {dep_airport} → To: {arr_airport}\n"
            f"Seat: {seat_number}\n\n"
            f"Attached is your e-ticket.\n\n"
            f"Thank you for choosing LastaMi!"
        )

        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email="kanteravali3@gmail.com",
            to=[email],
        )
        email_message.attach(f"SkyFinder_Ticket_{booking.id}.pdf", pdf_buffer.getvalue(), "application/pdf")

        try:
            email_message.send()
            messages.success(request, "Flight booked successfully! Confirmation email sent.")
        except Exception as e:
            messages.warning(request, f"Flight booked, but email failed to send: {e}")

        # ✅ Pass booking data to template
        context = {
            "airline": airline,
            "source": dep_airport,
            "destination": arr_airport,
            "price": price,
            "fullname": fullname,
            "seat_number": seat_number,
            "booking_id": booking.id,
        }
        return render(request, "flights/confirm_payment.html", context)

    return redirect("search_flights")


def support(request):
    return render(request,"support/support.html")


"""

@login_required
def payment(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Just show the payment/booking form (no filtering yet)
    context = {
        'hotel': hotel,
        'amount': hotel.price,
    }
    return render(request, "payment.html", context)


@login_required
def confirm_checkin_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        guest_name = request.POST.get('guest_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        address_proof = request.FILES.get('address_proof')

        # Convert date strings
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Invalid date format.")
            return redirect('payment', hotel_id=hotel.id)

        if check_in_date >= check_out_date:
            messages.error(request, "Check-out date must be after check-in date.")
            return redirect('payment', hotel_id=hotel.id)

        # ✅ Find available room for the given range
        available_room = None
        for room in Room.objects.filter(hotel=hotel):
            overlapping = Booking.objects.filter(
                room=room,
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            ).exists()
            if not overlapping:
                available_room = room
                break

        if not available_room:
            messages.error(request, "No available rooms for those dates.")
            return redirect('payment', hotel_id=hotel.id)

        # ✅ Create booking
        booking = Booking.objects.create(
            user=request.user,
            hotel=hotel,
            room=available_room,
            name=guest_name,
            check_in=check_in_date,
            check_out=check_out_date,
            num_persons=1,
            address_proof=address_proof,
        )

        # ✅ Send confirmation email
        subject = f"Booking Confirmation - {booking.id}"
        message = (
            f"Dear {guest_name},\n\n"
            f"Your booking at {hotel.name} is confirmed.\n"
            f"Booking ID: {booking.id}\n"
            f"Hotel: {hotel.name}\n"
            f"Check-in: {booking.check_in}\n"
            f"Check-out: {booking.check_out}\n"
            f"Please show this Booking ID at the hotel reception.\n\n"
            f"Thank you for choosing us!"
        )
        try:
            if email:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception:
            messages.warning(request, "Booking created but email could not be sent (check mail settings).")

        messages.success(request, f"✅ Booking confirmed! Your Booking ID is {booking.id}")
        return redirect('booking_conformed', hotel_id=hotel.id)

    return redirect('payment', hotel_id=hotel.id)

"""

@login_required
def booking_conformed(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, "booking_conformed.html", {"hotel": hotel})





# ✅ Show payment page — 30% auto-calculated
@login_required
def payment(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Automatically calculate 30% advance
    advance_amount = (hotel.price * Decimal('0.30')).quantize(Decimal('0.01'))
    remaining_amount = (hotel.price - advance_amount).quantize(Decimal('0.01'))

    context = {
        'hotel': hotel,
        'advance_amount': advance_amount,
        'remaining_amount': remaining_amount,
    }
    return render(request, "payment.html", context)


# ✅ Confirm booking after advance payment
@login_required
def confirm_checkin_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        guest_name = request.POST.get('guest_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        address_proof = request.FILES.get('address_proof')

        # Convert string to date
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Invalid date format.")
            return redirect('payment', hotel_id=hotel.id)

        if check_in_date >= check_out_date:
            messages.error(request, "Check-out date must be after check-in date.")
            return redirect('payment', hotel_id=hotel.id)

        # ✅ Find available room
        available_room = None
        for room in Room.objects.filter(hotel=hotel):
            overlapping = Booking.objects.filter(
                room=room,
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            ).exists()
            if not overlapping:
                available_room = room
                break

        if not available_room:
            messages.error(request, "No available rooms for those dates.")
            return redirect('payment', hotel_id=hotel.id)

        # ✅ Auto calculate amounts
        total_price = Decimal(hotel.price)
        advance_paid = (total_price * Decimal('0.30')).quantize(Decimal('0.01'))
        remaining_amount = (total_price - advance_paid).quantize(Decimal('0.01'))

        # ✅ Create booking
        booking = Booking.objects.create(
            user=request.user,
            hotel=hotel,
            room=available_room,
            name=guest_name,
            check_in=check_in_date,
            check_out=check_out_date,
            num_persons=1,
            address_proof=address_proof,  # ⚠️ match your model spelling
            advance_paid=advance_paid,
            remaining_amount=remaining_amount,
        )

        # ✅ Send confirmation email
        subject = f"Booking Confirmation - {booking.booking_id}"
        message = (
            f"Dear {guest_name},\n\n"
            f"Your booking at {hotel.name} is confirmed.\n"
            f"Booking ID: {booking.booking_id}\n"
            f"Hotel: {hotel.name}\n"
            f"Check-in: {booking.check_in}\n"
            f"Check-out: {booking.check_out}\n"
            f"Advance Paid: ₹{advance_paid}\n"
            f"Remaining Amount: ₹{remaining_amount} (payable at check-in)\n\n"
            f"Thank you for booking with us!"
        )
        try:
            if email:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception:
            messages.warning(request, "Booking confirmed, but email could not be sent.")

        messages.success(request, f"✅ Booking confirmed! ₹{advance_paid} paid successfully.")
        return redirect('booking_conformed', hotel_id=hotel.id)

    return redirect('payment', hotel_id=hotel.id)
