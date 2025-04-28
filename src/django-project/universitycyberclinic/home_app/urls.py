from django.urls import path
from . import views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    home, register_view, login_view, logout_view,
    appointment_view, receipt_view, download_receipt_pdf,
    resources, contact, about, services, networking, cloudsecurity,dataprotection,
    incidentresponseforensics, complianceandriskmanagement, trainingandwareness,
    ransomwareprotectionandresponse,
    user_dashboard, cancel_appointment,
    edit_profile, admin_dashboard, mark_appointment_completed,
    export_appointments_csv, assign_appointment_staff, admin_appointments_view,
    admin_users_view, edit_user_view, delete_user_view, login_as_staff, verify_email,
    resend_verification_email,
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
    path("networking/", networking, name="networking"),
    path("cloudsecurity/",cloudsecurity, name="cloudsecurity"),
    path("dataprotection/",dataprotection, name="dataprotection"),
    path("incidentresponseforensics/",incidentresponseforensics, name="incidentresponseforensics"),
    path("complianceandriskmanagement/",complianceandriskmanagement, name="complianceandriskmanagement"),
    path("trainingandwareness/",trainingandwareness, name="trainingandwareness"),
    path ("ransomwareprotectionandresponse/",ransomwareprotectionandresponse, name="ransomwareprotectionandresponse"),

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
    path('admin-dashboard/users/<int:user_id>/reset-password/', CustomPasswordResetView.as_view(), name='reset_user_password'),
    path('admin-dashboard/users/<int:user_id>/delete/', delete_user_view, name='delete_user'),
    path('login-as-staff/<int:user_id>/', login_as_staff, name='login_as_staff'),
    path('admin-dashboard/messages/', views.admin_contact_messages, name='admin_contact_messages'),

    # --- Email Verification ---
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),

    # Password reset URLs
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin-dashboard/messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('admin-dashboard/messages/<int:pk>/', views.admin_contact_message_detail, name='admin_contact_message_detail'),
    path('admin-dashboard/messages/<int:pk>/delete/', views.delete_contact_message, name='delete_contact_message'),
    path('admin-dashboard/messages/<int:pk>/', views.admin_contact_message_detail, name='admin_contact_message_detail'),
    path('admin-dashboard/messages/unread/', views.unread_message_count, name='unread_message_count'),
    path('admin-dashboard/messages/<int:pk>/mark-read/', views.mark_message_as_read, name='mark_message_as_read'),

]
