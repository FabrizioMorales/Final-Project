from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'appointment_date', 'appointment_time', 'details')
