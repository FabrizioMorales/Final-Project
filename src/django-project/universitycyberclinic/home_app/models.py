from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Appointment(models.Model):
    # ✅ Optional link to a registered user (for dashboard filtering)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)  # For the user's name
    email = models.EmailField()              # For the user's email
    appointment_date = models.DateField()    # For the date of the appointment
    appointment_time = models.TimeField()    # For the time of the appointment
    details = models.TextField(blank=True, null=True)  # For additional appointment details

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Added the assigned_staff field to track who handles the appointment
    assigned_staff = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.appointment_date} at {self.appointment_time}"

# ✅ User Profile linked to Django's built-in User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    business = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    last_verification_email_sent = models.DateTimeField(null=True, blank=True)  # ⏰ NEW FIELD


    def __str__(self):
        return f"{self.user.username} Profile"

