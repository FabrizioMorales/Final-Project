from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from xhtml2pdf import pisa
from io import BytesIO
import qrcode
import base64
from .models import Appointment, UserProfile
from .forms import AppointmentForm, RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from .forms import ProfileForm


# Home Page
def home(request):
    context = {
        'welcome_msg': "Welcome to the University Cyber and Technology Clinic! Empowering Our Community Through Technology and Security. At the University Cyber and Technology Clinic, we are dedicated to strengthening the technological capabilities of our local community and small to medium-sized enterprises (SMEs)."
    }
    return render(request, 'home.html', context)


# Static Pages
def resources(request):
    return render(request, 'resources.html', {'welcome_msg': "Welcome to resource page"})

def contact(request):
    return render(request, 'contact.html', {'welcome_msg': "Welcome to Contact page"})

def about(request):
    return render(request, 'about.html', {'welcome_msg': "Welcome to our about page"})

def services(request):
    return render(request, 'services.html', {'welcome_msg': "Welcome to our Services"})


# Appointment Booking (Requires Login)
@login_required
def appointment(request):
    return render(request, 'appointment.html', {'welcome_msg': "Welcome to our appointment page"})

@login_required
def appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            return redirect('receipt', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'appointment_form.html', {'form': form})


# User Registration
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Please log in instead.")
                return render(request, "register.html", {"form": form})

            # ✅ Save user data
            user = form.save(commit=False)
            user.username = email
            user.email = email
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()

            # ✅ Create or update UserProfile
            phone = form.cleaned_data.get("phone", "")
            business = form.cleaned_data.get("business", "")
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"phone": phone, "business": business}
            )

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# User Login (Using Email Instead of Username)
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(email=email).first()

        if user is not None:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect("user_dashboard")
            else:
                messages.error(request, "Invalid credentials. Please try again.")
        else:
            messages.error(request, "No account found with this email.")

    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


# User Logout
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")


# QR Code Generator
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_string = base64.b64encode(buffer.getvalue()).decode()
    return image_string


# Receipt Page
@login_required
def receipt_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    qr_data = f"Appointment ID: {appointment.id}\nName: {appointment.name}\nDate: {appointment.appointment_date}\nTime: {appointment.appointment_time}"
    qr_code = generate_qr_code(qr_data)
    return render(request, 'receipt.html', {
        'appointment': appointment,
        'qr_code': qr_code
    })


# PDF Receipt Download
@login_required
def download_receipt_pdf(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    qr_data = f"Appointment ID: {appointment.id}\nName: {appointment.name}\nDate: {appointment.appointment_date}\nTime: {appointment.appointment_time}"
    qr_code = generate_qr_code(qr_data)

    template = get_template('receipt_pdf.html')
    context = {
        'appointment': appointment,
        'qr_code': qr_code
    }
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="appointment_receipt_{appointment.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('PDF generation error')
    return response


# 🌟 User Dashboard
@login_required
def user_dashboard(request):
    user = request.user
    upcoming_appointments = Appointment.objects.filter(user=user, appointment_date__gte=datetime.now().date()).order_by('appointment_date')
    past_appointments = Appointment.objects.filter(user=user, appointment_date__lt=datetime.now().date()).order_by('-appointment_date')[:5]

    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'dashboard.html', context)


# Cancel Appointment
@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    appointment.delete()
    messages.success(request, "Appointment cancelled successfully.")
    return HttpResponseRedirect(reverse('user_dashboard'))

@login_required
def edit_profile(request):
    user = request.user
    profile = user.userprofile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_dashboard')
    else:
        form = ProfileForm(instance=profile, user=user)

    return render(request, 'profile.html', {'form': form})