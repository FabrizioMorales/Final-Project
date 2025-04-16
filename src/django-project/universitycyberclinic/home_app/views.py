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
import csv
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

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

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

@staff_member_required
def admin_dashboard(request):
    from home_app.models import Appointment

    total_users = User.objects.count()
    total_appointments = Appointment.objects.count()
    recent_appointments = Appointment.objects.order_by('-appointment_date', '-appointment_time')[:10]

    context = {
        'total_users': total_users,
        'total_appointments': total_appointments,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'admin_dashboard.html', context)


@staff_member_required
def mark_appointment_completed(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    appointment.status = "completed"
    appointment.assigned_staff = request.user.get_full_name() or request.user.username
    appointment.save()

    messages.success(request, f"Marked appointment #{appointment.id} as completed.")
    return redirect('admin_dashboard')

@staff_member_required
def export_appointments_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'User', 'Email', 'Date', 'Time',
        'Details', 'Status', 'Assigned Staff'
    ])

    appointments = Appointment.objects.all().order_by('-appointment_date')

    for appt in appointments:
        writer.writerow([
            appt.id,
            appt.name,
            appt.email,
            appt.appointment_date,
            appt.appointment_time,
            appt.details,
            appt.status,
            appt.assigned_staff or ''
        ])

    return response

@staff_member_required
@require_POST
def assign_appointment_staff(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    assigned_to = request.POST.get('assigned_staff')

    if assigned_to:
        appointment.assigned_staff = assigned_to
        appointment.save()
        messages.success(request, f"Assigned appointment #{appointment.id} to {assigned_to}")
    else:
        messages.error(request, "Please provide a staff name.")

    return redirect('admin_dashboard')

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_appointments = Appointment.objects.count()
    recent_appointments = Appointment.objects.order_by('-appointment_date', '-appointment_time')[:20]
    staff_users = User.objects.filter(is_staff=True)

    context = {
        'total_users': total_users,
        'total_appointments': total_appointments,
        'recent_appointments': recent_appointments,
        'staff_users': staff_users,
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def admin_appointments_view(request):
    from .models import Appointment
    from django.contrib.auth.models import User

    recent_appointments = Appointment.objects.order_by('-appointment_date', '-appointment_time')
    staff_users = User.objects.filter(is_staff=True)

    context = {
        'recent_appointments': recent_appointments,
        'staff_users': staff_users,
    }
    return render(request, 'admin_appointments.html', context)

# Admin Users View
@staff_member_required
def admin_users_view(request):
    users = User.objects.all().order_by('-is_staff', 'last_name')
    return render(request, 'admin_users.html', {'users': users})

@staff_member_required
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_staff = bool(request.POST.get('is_staff'))
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('admin_users')

    return render(request, 'edit_user.html', {'user': user})

@staff_member_required
def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")

    return redirect('admin_users')

def login_as_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_staff:
        # If the user is already authenticated as staff, just log them in
        if request.user == user:
            login(request, user)
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
        else:
            # Authenticate and log the user in as staff
            user = authenticate(request, username=user.username, password=user.password)
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')  # Redirect to the admin dashboard after login
            else:
                messages.error(request, "Authentication failed.")
                return redirect('admin_dashboard')  # Redirect to admin dashboard on authentication failure
    else:
        # If the user is not staff, do not allow login as staff
        messages.error(request, "You must be a staff member to access the admin dashboard.")
        return redirect('user_dashboard')  # Redirect back to user dashboard if not staff