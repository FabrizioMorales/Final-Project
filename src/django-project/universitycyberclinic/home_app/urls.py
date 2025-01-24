from home_app import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('resources/', views.resources, name='resources'),
    path('appointment/', views.appointment_view, name='appointment'),
    path('receipt/<int:appointment_id>/', views.receipt_view, name='receipt'),
    path('download-receipt/<int:appointment_id>/', views.download_receipt_pdf, name='download_receipt_pdf'),
]
