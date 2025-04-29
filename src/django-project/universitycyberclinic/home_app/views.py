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
from datetime import datetime, timedelta
from .forms import ProfileForm
import csv
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm
from .forms import ContactForm
from .models import ContactMessage
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import EmailMessage
from datetime import date, time, datetime, timedelta
from django.http import HttpResponse
from icalendar import Calendar, Event
from pytz import timezone as pytz_timezone


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

def networking(request):
    return render(request, 'NetworkingSecurityAssessment.html', {'welcome_msg': "Welcome to our Networking Security Assessment Page"})

def cloudsecurity(request):
    return render(request, 'CloudSecurity.html', {'welcome_msg': "Welcome to our Cloud Security Page"})

def dataprotection(request):
    return render(request, 'dataprotection.html', {'welcome_msg': "Welcome to our Data Protection and Recovery Page"})

def incidentresponseforensics(request):
    return render(request, 'incidentresponseforensics.html', {'welcome_msg': "Welcome to our Incident Response and Forensics Page"})

def complianceandriskmanagement(request):
    return render(request, 'complianceandriskmanagement.html', {'welcome_msg': "Welcome to our Compliance and Risk Management Page"})

def trainingandwareness(request):
    return render(request, 'trainingandwareness.html', {'welcome_msg': "Welcome to our Training and Awareness Page"})

def ransomwareprotectionandresponse(request):
    return render(request, 'ransomwareprotectionandresponse.html', {'welcome_msg': "Welcome to our Ransomware Protection and Response Page"})

def physicalsecurityintegration(request):
    return render(request, 'physicalsecurityintegration.html', {'welcome_msg': "Welcome to our Physical Security Integration Page"})

def cybersecurityconsulting(request):
    return render(request, 'cybersecurityconsulting.html', {'welcome_msg': "Welcome to our Cybersecurity Consulting Page"})

# Appointment Booking (Requires Login)
# ✅ API: Return available slots
def available_slots_api(request):
    selected_date = request.GET.get('date')

    if not selected_date:
        return JsonResponse({'error': 'Date is required.'}, status=400)

    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)

    # Block weekends
    if selected_date.weekday() in [5, 6]:
        return JsonResponse({'available_slots': []})

    slots = [time(h, m) for h in range(10, 17) for m in (0, 30)]
    slots.append(time(16, 30))

    booked = Appointment.objects.filter(
        appointment_date=selected_date
    ).values_list('appointment_time', flat=True)

    available = [t.strftime('%H:%M') for t in slots if t not in booked]

    if selected_date == date.today():
        now = datetime.now().time()
        available = [t for t in available if datetime.strptime(t, "%H:%M").time() > now]

    return JsonResponse({'available_slots': available})

# ✅ PDF Receipt Generator
def generate_receipt_pdf(appointment):
    template = get_template('receipt_pdf.html')
    html = template.render({'appointment': appointment})
    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    return buffer.getvalue()

# ✅ Appointment Booking
@login_required
def appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user

            today = timezone.now().date()
            now = timezone.now().time()

            # Validate
            if appointment.appointment_date < today:
                form.add_error('appointment_date', "Cannot book past dates.")
            elif appointment.appointment_date.weekday() in [5, 6]:
                form.add_error('appointment_date', "We are closed on weekends.")
            elif appointment.appointment_date == today and appointment.appointment_time <= now:
                form.add_error('appointment_time', "Time must be in the future.")
            elif Appointment.objects.filter(
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time
            ).exists():
                form.add_error('appointment_time', "Slot already booked.")
            else:
                appointment.save()

                # ✅ Email with PDF
                pdf = generate_receipt_pdf(appointment)
                email = EmailMessage(
                    subject='Your Appointment Receipt - University Cyber Clinic',
                    body=render_to_string('emails/appointment_confirmation.html', {
                        'appointment': appointment,
                        'rescheduled': False,
                        'domain': request.get_host()
                    }),
                    to=[appointment.email]
                )
                email.attach('appointment_receipt.pdf', pdf, 'application/pdf')
                email.content_subtype = 'html'
                email.send()

                messages.success(request, "Appointment booked! Receipt sent.")
                return redirect('receipt', appointment_id=appointment.id)
        else:
            messages.error(request, "Please fix errors below.")
    else:
        form = AppointmentForm()

    slots = [time(h, m).strftime('%H:%M') for h in range(10, 17) for m in (0, 30)]
    slots.append("16:30")

    return render(request, 'appointment_form.html', {
        'form': form,
        'available_times': slots
    })

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save()

            # ✅ Generate updated PDF receipt
            pdf = generate_receipt_pdf(appointment)

            # ✅ Email confirmation with receipt
            email = EmailMessage(
                subject="📅 Appointment Rescheduled – University Cyber Clinic",
                body=render_to_string("emails/appointment_confirmation.html", {
                    "appointment": appointment,
                    "rescheduled": True,
                    'domain': request.get_host()
                }),
                to=[appointment.email]
            )
            email.attach('updated_appointment_receipt.pdf', pdf, 'application/pdf')
            email.content_subtype = 'html'
            email.send()

            messages.success(request, "Appointment rescheduled successfully. A confirmation has been sent.")
            return redirect("receipt", appointment_id=appointment.id)
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = AppointmentForm(instance=appointment)

    # Reuse time slots (10:00 - 4:30)
    slots = [time(h, m).strftime('%H:%M') for h in range(10, 17) for m in (0, 30)]
    slots.append("16:30")

    return render(request, 'reschedule_appointment.html', {
        'form': form,
        'available_times': slots,
        'rescheduling': True
    })


@login_required
def download_ics(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    cal = Calendar()
    event = Event()

    dt_start = datetime.combine(appointment.appointment_date, appointment.appointment_time)
    dt_end = dt_start + timedelta(minutes=30)
    tz = pytz_timezone("Europe/London")

    event.add('summary', 'Cyber Clinic Appointment')
    event.add('dtstart', tz.localize(dt_start))
    event.add('dtend', tz.localize(dt_end))
    event.add('dtstamp', datetime.now())
    event.add('location', 'University Cyber Clinic')
    event.add('description', appointment.details or 'Consultation appointment')

    cal.add_component(event)

    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename=appointment_{appointment.id}.ics'
    return response

# User Registration
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Please log in instead.")
                return render(request, "register.html", {"form": form})

            # ✅ Save user as inactive
            user = form.save(commit=False)
            user.username = email
            user.email = email
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.is_active = False  # 🔒 Important for verification
            user.save()

            # ✅ Create or update UserProfile
            phone = form.cleaned_data.get("phone", "")
            business = form.cleaned_data.get("business", "")
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"phone": phone, "business": business}
            )

            # ✅ Send verification email
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_url = f"http://{current_site.domain}/verify-email/{uid}/{token}/"

            subject = "Verify your email - University Cyber Clinic"
            message = render_to_string("email_verification.html", {
                "first_name": user.first_name,
                "verify_url": verify_url
            })

            send_mail(
                subject,
                message,
                "noreply@universitycyber.uk",
                [user.email],
                fail_silently=False
            )

            messages.success(request, "Registration successful. Please check your email to verify your account.")
            return redirect("login")

        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

def verify_email(request, uidb64, token):
    try:
        # Decode the UID from the URL and retrieve the user
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)

        # Check if the token is valid for the user
        if default_token_generator.check_token(user, token):
            user.is_active = True  # Mark user as active (email verified)
            user.save()

            # Log the user in after verification
            login(request, user)
            
            messages.success(request, 'Email verified! You are now logged in.')
            return redirect('user_dashboard')  # Redirect to user dashboard after login

        else:
            messages.error(request, 'Invalid or expired verification link.')
            return redirect('register')

    except Exception as e:
        messages.error(request, 'Something went wrong during email verification.')
        return redirect('register')

#resend verification email
def resend_verification_email(request):
    class ResendVerificationForm(forms.Form):
        email = forms.EmailField(label="Enter your email")

    if request.method == "POST":
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                profile, _ = UserProfile.objects.get_or_create(user=user)

                if user.is_active:
                    messages.info(request, "This account is already verified. Please log in.")
                    return redirect("login")

                # ✅ Rate limit check
                now = timezone.now()
                if profile.last_verification_email_sent and now - profile.last_verification_email_sent < timedelta(seconds=60):
                    remaining_time = 60 - (now - profile.last_verification_email_sent).seconds
                    messages.warning(request, f"You can only resend the email after {remaining_time} seconds.")
                    return redirect("resend_verification")

                # ✅ Send email
                current_site = get_current_site(request)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                verify_url = f"http://{current_site.domain}/verify-email/{uid}/{token}/"

                subject = "Resend Verification Email - University Cyber Clinic"
                message = render_to_string("email_verification.html", {
                    "first_name": user.first_name,
                    "verify_url": verify_url
                })

                send_mail(subject, message, "noreply@universitycyber.uk", [user.email])

                # ✅ Update timestamp
                profile.last_verification_email_sent = now
                profile.save()

                messages.success(request, "A new verification email has been sent!")
                return redirect("login")  # ✅ Auto-redirect after success

            except User.DoesNotExist:
                messages.error(request, "No account found with that email.")
                return redirect("resend_verification")

    else:
        form = ResendVerificationForm()

    return render(request, "resend_verification.html", {"form": form})

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


from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm
# 🌟 Class-Based Password Reset Views (Enhanced)
class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'reg/password_reset_form.html'
    email_template_name = 'reg/password_reset_email.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email', '')
        domain = email.split('@')[-1].lower()
        return redirect(f"{reverse('password_reset_done')}?provider={domain}")


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'reg/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'reg/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'reg/password_reset_complete.html'

# User Logout
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")

#contanct form
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # 1. Save to DB
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # 2. Compose email content
            full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

            # 3. Send email to admin
            send_mail(
                subject=f"[Contact Form] {subject}",
                message=full_message,
                from_email="noreply@universitycyber.uk",
                recipient_list=["info@universitycyber.uk"],
                fail_silently=False,
            )

            # 4. Send copy to user
            send_mail(
                subject="Copy of your message to University Cyber Clinic",
                message=f"Hi {name},\n\nHere's a copy of your message:\n\n{full_message}\n\nWe'll get back to you shortly!",
                from_email="noreply@universitycyber.uk",
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent! A copy was sent to your email.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


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

    # Save the user's email BEFORE deleting the appointment
    user_email = appointment.email
    user_name = appointment.name
    appointment_date = appointment.appointment_date
    appointment_time = appointment.appointment_time

    appointment.delete()

    # Send cancellation email
    subject = "🚫 Appointment Cancelled - University Cyber Clinic"
    message = render_to_string('emails/cancellation_confirmation.html', {
        'name': user_name,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time,
        'domain': request.get_host(),
    })

    email = EmailMessage(
        subject,
        message,
        to=[user_email]
    )
    email.content_subtype = 'html'
    email.send()

    messages.success(request, "Appointment cancelled and confirmation sent.")
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

def admin_dashboard(request):
    total_users = User.objects.count()
    total_appointments = Appointment.objects.count()
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(read=False).count()
    read_messages = ContactMessage.objects.filter(read=True).count()

    context = {
        'total_users': total_users,
        'total_appointments': total_appointments,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'read_messages': read_messages,
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
    new_assigned_to = request.POST.get('assigned_staff')

    if new_assigned_to:
        previous_assigned = appointment.assigned_staff
        appointment.assigned_staff = new_assigned_to
        appointment.save()

        # Try resolving both staff User objects
        def resolve_user_by_name(name):
            try:
                first, last = name.split(' ', 1)
                return User.objects.filter(first_name=first, last_name=last).first()
            except ValueError:
                return User.objects.filter(username=name).first()

        new_staff_user = resolve_user_by_name(new_assigned_to)
        previous_staff_user = resolve_user_by_name(previous_assigned) if previous_assigned != new_assigned_to else None

        # ✅ Email to newly assigned staff
        if new_staff_user:
            subject = f"New Appointment Assigned - #{appointment.id}"
            message = render_to_string('emails/staff_assignment_notification.html', {
                'appointment': appointment,
                'staff': new_staff_user,
                'assignment_type': 'assigned',
                'domain': request.get_host()
            })
            email = EmailMessage(subject, message, "noreply@universitycyber.uk", [new_staff_user.email])
            email.content_subtype = "html"
            email.send()

        # ✅ Email to unassigned previous staff
        if previous_staff_user:
            subject = f"Appointment Unassigned - #{appointment.id}"
            message = render_to_string('emails/staff_assignment_notification.html', {
                'appointment': appointment,
                'staff': previous_staff_user,
                'assignment_type': 'unassigned',
                'domain': request.get_host()
            })
            email = EmailMessage(subject, message, "noreply@universitycyber.uk", [previous_staff_user.email])
            email.content_subtype = "html"
            email.send()

        messages.success(request, f"Appointment #{appointment.id} assigned to {new_assigned_to}")
    else:
        messages.error(request, "No staff selected for assignment.")

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
    

@staff_member_required
def admin_contact_messages(request):
    messages = ContactMessage.objects.order_by('-created_at')
    return render(request, 'admin_contact_messages.html', {'messages': messages})


@staff_member_required
def admin_contact_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'admin_contact_messages.html', {'messages': messages})

@staff_member_required
def admin_contact_message_detail(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    return render(request, 'admin_contact_message_detail.html', {'message': message})

@staff_member_required
def delete_contact_message(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    message.delete()
    messages.success(request, "Message deleted successfully.")
    return redirect('admin_contact_messages')


from django.core.paginator import Paginator

@staff_member_required
def admin_contact_messages(request):
    query = request.GET.get('q', '')
    subject_filter = request.GET.get('subject', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    messages = ContactMessage.objects.all()

    if query:
        messages = messages.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query)
        )

    if subject_filter:
        messages = messages.filter(subject=subject_filter)

    if date_from:
        messages = messages.filter(created_at__date__gte=date_from)
    if date_to:
        messages = messages.filter(created_at__date__lte=date_to)

    subjects = ContactMessage.objects.values_list('subject', flat=True).distinct()

    # ✅ Apply pagination
    paginator = Paginator(messages.order_by('-created_at'), 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_contact_messages.html', {
        'page_obj': page_obj,
        'subjects': subjects,
        'query': query,
        'subject_filter': subject_filter,
        'date_from': date_from,
        'date_to': date_to,
    })

def unread_message_count(request):
    unread_count = ContactMessage.objects.filter(read=False).count()
    return JsonResponse({'unread_count': unread_count})

@staff_member_required
def unread_message_count(request):
    count = ContactMessage.objects.filter(read=False).count()
    return JsonResponse({'unread_count': count})

@staff_member_required
def mark_message_as_read(request, pk):
    try:
        msg = ContactMessage.objects.get(pk=pk)
        msg.read = True
        msg.save()
        return JsonResponse({'success': True})
    except ContactMessage.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
    
