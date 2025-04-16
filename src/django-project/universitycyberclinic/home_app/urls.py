from django.urls import path
from django.contrib.auth.views import PasswordResetView
from .views import (
    home, register_view, login_view, logout_view,
    appointment_view, receipt_view, download_receipt_pdf,
    resources, contact, about, services,
    user_dashboard, cancel_appointment,
    edit_profile, admin_dashboard, mark_appointment_completed,
    export_appointments_csv, assign_appointment_staff, admin_appointments_view,
    admin_users_view, edit_user_view, delete_user_view, login_as_staff,
)

urlpatterns = [
    # --- Auth ---
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # --- Public Pages ---
    path("", home, name="home"),
    path("resources/", resources, name="resources"),
    path("contact/", contact, name="contact"),
    path("about/", about, name="about"),
    path("services/", services, name="services"),

    # --- Appointments (User) ---
    path("appointment/", appointment_view, name="appointment"),
    path("receipt/<int:appointment_id>/", receipt_view, name="receipt"),
    path("download-receipt/<int:appointment_id>/", download_receipt_pdf, name="download_receipt_pdf"),
    path("cancel-appointment/<int:appointment_id>/", cancel_appointment, name="cancel_appointment"),

    # --- User Profile & Dashboard ---
    path("dashboard/", user_dashboard, name="user_dashboard"),
    path("profile/", edit_profile, name="edit_profile"),

    # --- Admin Dashboard & Views ---
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/appointments/", admin_appointments_view, name="admin_appointments"),
    path("dashboard/appointments/<int:appointment_id>/complete/", mark_appointment_completed, name="mark_appointment_completed"),
    path("dashboard/appointments/<int:appointment_id>/assign/", assign_appointment_staff, name="assign_appointment_staff"),
    path("dashboard/export/appointments/", export_appointments_csv, name="export_appointments_csv"),
    path('admin-dashboard/users/', admin_users_view, name='admin_users'),
    path('admin-dashboard/users/<int:user_id>/edit/', edit_user_view, name='edit_user'),
    path('admin-dashboard/users/<int:user_id>/reset-password/', PasswordResetView.as_view(), name='reset_user_password'),
    path('admin-dashboard/users/<int:user_id>/delete/', delete_user_view, name='delete_user'),
    path('login-as-staff/<int:user_id>/', login_as_staff, name='login_as_staff'),
]
