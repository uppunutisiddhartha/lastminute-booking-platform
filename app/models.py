from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
from django.utils import timezone
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
from django.db import models
from django.conf import settings
import uuid


# -------------------------
# Hotel Model
# -------------------------
class Hotel(models.Model):
    dealer = models.ForeignKey('Dealer', on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True, help_text="Total number of rooms in the hotel")
    ac_room_count = models.PositiveIntegerField(default=0)
    non_ac_room_count = models.PositiveIntegerField(default=0)

    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=False)
    has_restaurant = models.BooleanField(default=False)
    has_dining = models.BooleanField(default=False)
    has_elevator = models.BooleanField(default=False)
    has_cctv = models.BooleanField(default=False)
    has_room_service = models.BooleanField(default=False)
    has_swimming_pool = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)

    extra_amenities = models.JSONField(default=list, blank=True)
    floor_count = models.PositiveIntegerField(default=1)
    hotel_image = models.ImageField(upload_to='hotel_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


# -------------------------
# Room Model (Auto-generated per Hotel)
# -------------------------
class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('AC', 'AC Room'),
        ('NON_AC', 'Non-AC Room'),
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    #price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_booked = models.BooleanField(default=False)
    booked_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.room_number} - {self.hotel.name}"



# -------------------------
# Booking Model
# -------------------------
"""

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=15)
    email = models.EmailField()
    check_in = models.DateField()
    check_out = models.DateField()
    num_persons = models.PositiveIntegerField(default=1)
    address_proof = models.FileField(upload_to='address_proofs/', null=True, blank=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    booking_id = models.CharField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BK{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.hotel.name} ({self.check_in} → {self.check_out})"



class payment(models.Model):
    PAYMENT_STATUS=(
        ('Pending','Pending'),
        ('Success','Success'),
        ('Failed','Failed'),
    )
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    Hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE)
    Room=models.ForeignKey(Room,on_delete=models.CASCADE)
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    payment_date=models.DateTimeField(auto_now_add=True)
    payment_status=models.CharField(max_length=10,choices=PAYMENT_STATUS,default='Pending')
    transaction_id=models.CharField(max_length=50,unique=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.payment_status}"

"""
# models.py
from django.db import models
from django.conf import settings

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True, blank=True)
    
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=[
        ('Advance', 'Advance Payment'),
        ('Final', 'Final Payment')
    ], default='Advance')
    payment_status = models.CharField(max_length=20, default='Success')
    transaction_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.payment_type} - {self.amount}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    address_proof = models.FileField(upload_to='address_proofs/', null=True, blank=True)
    name = models.CharField(max_length=100)
    check_in = models.DateField()
    check_out = models.DateField()
    num_persons = models.PositiveIntegerField(default=1)
    
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_checked_out = models.BooleanField(default=False)
    booking_id = models.CharField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BK{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} - {self.hotel.name}"



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




#support 
class support_chat(models.Model):
    Chat_status=(
        ('pending','penging'),
        ('Resolved','Resolved'),
    )
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    requested_date=models.DateTimeField()
    TimeDuration=models.DurationField()
    Chat_reference_number=models.CharField(max_length=10,blank=False,unique=True)
    Chat_status=models.CharField(max_length=10,choices=Chat_status,blank=False)
    
    def save(self, *args, **kwargs):
        if not self.Chat_reference_number:
            self.Chat_reference_number = f"Chat{uuid.uuid4().hex[:7].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}-{self._state}-{self.Chat_reference_number}"
    


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.hotel} ({self.rating})"