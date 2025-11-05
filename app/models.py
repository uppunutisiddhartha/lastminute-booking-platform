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

from django.db import models

class Hotel(models.Model):
    
    dealer = models.ForeignKey('Dealer', on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, help_text="Brief description about the hotel, nearby attractions, etc.")
    number_of_rooms=models.IntegerField(null=True,blank=True,unique=True)
    ac_room_count = models.PositiveIntegerField(default=0,help_text="Number of air-conditioned rooms.")
    non_ac_room_count = models.PositiveIntegerField(default=0,help_text="Number of non air-conditioned rooms.")

    # Common facilities (boolean fields for clarity and filtering)
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

    # Optional: JSON field for any extra amenities not covered above
    extra_amenities = models.JSONField(default=list, blank=True)

    floor_count = models.PositiveIntegerField(
        default=1, 
        help_text="Total number of floors in the hotel"
    )
    hotel_image = models.ImageField(
        upload_to='hotel_images/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.location}"




class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel_room = models.ForeignKey(Hotel, on_delete=models.CASCADE)
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

# class Airline(models.Model):
#     name = models.CharField(max_length=100)
#     code = models.CharField(max_length=10, unique=True)
#     def __str__(self):
#         return self.name

# class Flight(models.Model):
#     airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
#     flight_number = models.CharField(max_length=10)
#     source = models.CharField(max_length=50)
#     destination = models.CharField(max_length=50)
#     departure_time = models.DateTimeField()
#     arrival_time = models.DateTimeField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     seats_available = models.IntegerField(default=100)
#     def __str__(self):
#         return f"{self.flight_number} ({self.source} → {self.destination})"
    



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