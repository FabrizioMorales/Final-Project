from django.urls import path
from .views import (
    home, register_view, login_view, logout_view, 
    appointment_view, receipt_view, download_receipt_pdf,
    resources, contact, about, services
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Authentication Routes
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Core Pages
    path("", home, name="home"),
    path("resources/", resources, name="resources"),
    path("contact/", contact, name="contact"),
    path("about/", about, name="about"),
    path("services/", services, name="services"),

    # Appointment Booking & Receipt
    path("appointment/", appointment_view, name="appointment"),
    path("receipt/<int:appointment_id>/", receipt_view, name="receipt"),
    path("download-receipt/<int:appointment_id>/", download_receipt_pdf, name="download_receipt"),
]
