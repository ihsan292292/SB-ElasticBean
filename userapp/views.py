from django.shortcuts import render,redirect
from django.http import response,HttpResponse
from .forms import *
from .models import contacted_user
from django.contrib import messages
from adminapp.models import *
from django.db.models import Q
from twilio.rest import Client
import os 

# Create your views here.

def INDEX(request):
    selected_courses = Course.objects.filter(
        Q(name__icontains='ADVANCE HOSPITAL ADMINISTRATION&FRONT OFFICE MANAGEMENT') |
        Q(name__icontains='IDBA (INTERNATIONAL DIPLOMA IN BUSINESS ACCOUNTING') |
        Q(name__icontains='HOSPITAL ADMINISTRATION&FRONT OFFICE MANAGEMENT')  |
        Q(name__icontains='OFFICE ADMINISTRATION') |
        Q(name__icontains='Python Django- Full Stack Web Development') 
    )
    staffs = Staff.objects.all()
    bgs = Bgimages.objects.all()
    home = Home.objects.all()
    testimonials = Testimonal.objects.all()
    branches = Branch.objects.all()
    logos = AffLogo.objects.all()
    img_gallery = ImgGallary.objects.all()
    
    # home = Home.objects.get(id=1)
    context = {
        'courses':selected_courses,
        'staffs':staffs,
        'bgs':bgs,
        'home':home,
        'testimonials':testimonials,
        'branches':branches,
        'logos':logos,
        'img_gallery':img_gallery
    }

    return render(request,'index.html',context=context)

    
def contact(request):
    courses = Course.objects.all()
    branches = Branch.objects.all()
    context = {
        'courses':courses,
        'branches':branches
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')  
        phone = request.POST.get('phone')  
        course_id = request.POST.get('course_id')
        message = request.POST.get('message')
        
        # Save form data to the user model
        course = Course.objects.get(id=course_id)
        user_object = contacted_user(name=name, email=email, phone=phone, course=course, message=message)
        user_object.save()
        try:
            # Sending WhatsApp message
            client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
            message = client.messages.create(
                from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                body=f'Hi *{name}*,\n*Thank You for Contacting Us!!\n\nHere is your enquiry course in Detail \n\n*{course.name}*\nDuration : {course.duration}\nYou will Learn : {course.description}\n\nFor Fee Details and any other Query\nfeel free to contact :+91 6238 627 545 \n\nHappy Learning ☺️📚📚!!\n\n*SKILLBOARD EDUCATION**',
                to=f'whatsapp:+91{phone}'  # Phone number of the student
            )
            print("WhatsApp message SID:", message.sid)  # Log the message SID for debugging
        except Exception as e:
            print("Error sending WhatsApp message:", e)

        messages.success(request,"Thank You for contacting us!!, we will contact you as soon as possible")
        return redirect('contact')
    else:
        return render(request,'contact.html',context=context)
    
def about(request):
    students = Student.objects.all().count()
    staffs = Staff.objects.all().count()
    courses = Course.objects.all().count()
    branches = Branch.objects.all()
    testimonials = Testimonal.objects.all()
    about = About.objects.first()
    team = Staff.objects.all()
    context = {
        'testimonials': testimonials,
        'about': about,
        'students': students,
        'staffs': staffs,
        'courses': courses,
        'branches': branches,
        'team': team
    }
    return render(request, 'about.html', context=context)


def course(request):
    about = Home.objects.all()
    courses = Course.objects.all()
    branches = Branch.objects.all()
    pho = []
    for i in courses:
        pho.append(i.photo)
    print(pho)
    context = {
        'courses':courses,
        'about':about,
        'branches':branches
    }
    return render(request,'courses.html',context=context)

# certificate verification

def certificate_issue(request):
    context = {}
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if Student.objects.filter(phone=phone).exists():
            student = Student.objects.get(phone=phone)
            context['student'] = student
        else:
            context['error'] = "Student not found."
    
    # Add branch information to the context
    branches = Branch.objects.all()
    context['branches'] = branches
    
    return render(request, 'certificate_issue.html', context)

def vacancies(request):
    placements = Placement.objects.all()
    context = {
        "placements":placements
    }
    return render(request,"placements.html",context)
