from django.shortcuts import render, redirect
from django.shortcuts import render
from django.http import HttpResponse
from .models import Appointment
from .forms import AppointmentForm

# Create your views here.

def home(request):  
    context ={'welcome_msg':"Welcome to the University Cyber and Technology Clinic! Empowering Our Community Through Technology and SecurityAt the University Cyber and Technology Clinic, we are dedicated to strengthening the technological capabilities of our local community and small to medium-sized enterprises (SMEs). Our mission is to bridge the gap between academic expertise and real-world challenges, offering comprehensive solutions in web development, mobile applications, operating systems, and cybersecurity. What We Offer: Web Development Services: Build and secure your online presence with our expert-designed, responsive websites tailored for your needs. Schedule a consultation today with our easy-to-use appointment system. Cybersecurity Solutions: Safeguard your digital assets with advanced security practices, workshops, and guides created to protect your business in the modern digital landscape. Training and Education: Enhance your team's skills with workshops and webinars on topics like SEO optimization, secure development practices, and website maintenance. Why Choose Us? Our clinic combines cutting-edge academic knowledge with practical expertise, fostering collaborations between students, faculty, and local businesses. By working with us, you’ll gain access to innovative solutions and educational resources designed to meet your unique challenges. Together, let’s build a safer, smarter digital future for our community."}
    return render(request, 'home.html', context)


def resources(request):  
    context ={'welcome_msg':"Welcome to resource page"}
    return render(request, 'resources.html', context)

def contact(request):  
    context ={'welcome_msg':"Welcome to Contact page"}
    return render(request, 'contact.html', context)

def about(request):  
    context ={'welcome_msg':"Welcome to our about page"}
    return render(request, 'about.html', context)

def appointment(request):  
    context ={'welcome_msg':"Welcome to our appointment page"} 
    return render(request, 'appointment.html', context)

def services(request):  
    context ={'welcome_msg':"Welcome to our Services"}
    return render(request, 'services.html', context)

def appointment_view(request):
    print("appointment_view is called")
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Save the appointment and redirect to the receipt page
            appointment = form.save()
            return redirect('receipt', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'home_app/appointment_form.html', {'form': form})

def receipt_view(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    return render(request, 'home_app/receipt.html', {'appointment': appointment})