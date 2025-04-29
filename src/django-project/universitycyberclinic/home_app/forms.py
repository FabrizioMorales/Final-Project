from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Appointment
from .models import UserProfile
from django.contrib.auth.forms import PasswordResetForm
from datetime import datetime, date, time, timedelta

# Appointment Booking Form
from django import forms
from .models import Appointment
from datetime import date, time, datetime

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'appointment_date', 'appointment_time', 'details']

        widgets = {
            'appointment_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full p-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400'
            }),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full p-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Appointment Details'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        # 🚨 Validate date
        if not appointment_date:
            raise forms.ValidationError("Please select a date.")

        today = date.today()
        if appointment_date < today:
            raise forms.ValidationError("You cannot book an appointment for a past date.")

        # 🚨 Validate time slot
        valid_slots = [
            time(hour, minute)
            for hour in range(10, 17)  # 10AM to 4PM
            for minute in (0, 30)
        ]
        valid_slots.append(time(16, 30))  # 4:30 PM slot

        if appointment_time not in valid_slots:
            raise forms.ValidationError("Invalid appointment time. Please select a valid 30-minute slot between 10:00 AM and 4:30 PM.")

        # 🚨 Validate no booking past time today
        now = datetime.now()
        if appointment_date == today:
            current_time = now.time()
            if appointment_time <= (current_time.replace(second=0, microsecond=0)):
                raise forms.ValidationError("You cannot book a slot earlier than the current time.")

        # 🚨 Validate no overlap
        if Appointment.objects.filter(
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exists():
            raise forms.ValidationError("This slot is already booked. Please select a different time.")

        return cleaned_data

class RescheduleAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time']
        
# User Registration Form (Username == Email)
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your forename'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your surname'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your contact number'})
    )
    business = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your business name (if applicable)'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Use email as username
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        
        if commit:
            user.save()

        # Capture extra fields if needed (e.g. log, use in profile, or email)
        phone = self.cleaned_data.get("phone")
        business = self.cleaned_data.get("business")
        print(f"Registered user phone: {phone}, business: {business}")

        return user


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Enter your email", widget=forms.EmailInput(attrs={
        'class': 'w-full p-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400',
        'placeholder': 'Enter your registered email address'
    }))

# User Login Form (Uses Email Instead of Username)
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'w-full p-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full p-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400', 'placeholder': 'Enter your password'})
    )

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone', 'business', 'profile_image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea)
    
from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Announcement
        fields = ['title', 'message', 'event_date']