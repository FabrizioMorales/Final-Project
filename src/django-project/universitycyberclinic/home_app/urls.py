from home_app import views
from django.urls import path
urlpatterns = [
    path('',views.home, name='home'),
    path('services',views.services, name='services'),
    path('about',views.about, name='about'),
    path('contact',views.contact, name='contact'),
    path('resources',views.resources, name='resources'),
    path('appointment',views.appointment, name='appointment')
    
    
]