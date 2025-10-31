from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('dealer', 'Dealer'),
        ('customer', 'Customer'),
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    state = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Dealer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name_of_company = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


# -------------------------
# Hotel & HotelRoom Models
# -------------------------

class Hotel(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    amenities = models.JSONField(default=list)
    description = models.TextField(null=True, blank=True)
    floor_count = models.PositiveIntegerField(default=1, help_text="Total number of floors in the hotel")
    Hotel_image=models.ImageField(upload_to='hotel_images/',null=True,blank=True)
    def __str__(self):
        return f"{self.name} - {self.location}"


# class HotelRoom(models.Model):
#     ROOM_TYPE_CHOICES = (
#         ('single', 'Single'),
#         ('double', 'Double'),
#         ('suite', 'Suite'),
#     )

#     hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
#     room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
#     price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
#     capacity = models.IntegerField()
#     available = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.hotel.name} - {self.room_type}"
    
class HotelRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    )
    #dealer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    floor_number = models.PositiveIntegerField(default=1)
    room_number = models.CharField(max_length=4)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, null=True, blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roomImg=models.ImageField(upload_to='room_images/',null=True,blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hotel.name} - Floor {self.floor_number} - Room {self.room_number}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel_room = models.ForeignKey(HotelRoom, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    name=models.CharField(max_length=50)
    Booking_id=models.IntegerField(unique=True , editable=False)
    num_persons = models.PositiveIntegerField(default=1)
    address_proof = models.FileField(upload_to='address_proofs/', null=True, blank=True)
    
    # auto generation for booking id which is uniqe 
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BK{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Booking for {self.hotel_room} from {self.check_in} to {self.check_out}"


# -------------------------
# Flight Model
# -------------------------

class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name

class Flight(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=10)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seats_available = models.IntegerField(default=100)
    def __str__(self):
        return f"{self.flight_number} ({self.source} → {self.destination})"
    



class Flight_Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Flight details
    flight_name = models.CharField(max_length=100)
    flight_no = models.CharField(max_length=20, blank=True, null=True)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    departure_time = models.CharField(max_length=50, blank=True, null=True)
    arrival_time = models.CharField(max_length=50, blank=True, null=True)

    # Passenger details
    passengers = models.PositiveIntegerField(default=1)
    passenger_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    # Payment details
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Success", "Success"), 
            ("Failed", "Failed")
        ],
        default="pending"
    )

    booked_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger_name} - {self.flight_name} ({self.source} → {self.destination})"
