from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    # ✅ Optional link to a registered user (for dashboard filtering)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)  # For the user's name
    email = models.EmailField()              # For the user's email
    appointment_date = models.DateField()    # For the date of the appointment
    appointment_time = models.TimeField()    # For the time of the appointment
    details = models.TextField(blank=True, null=True)  # For additional appointment details

    def __str__(self):
        return f"{self.name} - {self.appointment_date} at {self.appointment_time}"
