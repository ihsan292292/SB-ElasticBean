from django.shortcuts import render,redirect
from django.http import response,HttpResponse
from .forms import *
from .models import contacted_user
from django.contrib import messages
from adminapp.models import *
# Create your views here.

def INDEX(request):
    courses = Course.objects.all()
    staffs = Staff.objects.all()
    bgs = Bgimages.objects.all()
    home = Home.objects.all()
    testimonials = Testimonal.objects.all()
    # home = Home.objects.get(id=1)
    context = {
        'courses':courses,
        'staffs':staffs,
        'bgs':bgs,
        'home':home,
        'testimonials':testimonials
    }

    return render(request,'index.html',context=context)

    
def contact(request):
    courses = Course.objects.all()
    context = {
        'courses':courses
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
        
        messages.success(request,"Thank You for contacting us!!, we will contact you as soon as possible")
        return redirect('contact')
    else:
        return render(request,'contact.html',context=context)
    
def about(request):
    students = Student.objects.all().count()
    staffs = Staff.objects.all().count()
    courses = Course.objects.all().count()
    branches = Branch.objects.all().count()
    testimonials = Testimonal.objects.all()
    about = About.objects.first()
    team = Staff.objects.all()
    context = {
        'testimonials':testimonials,
        'about':about,
        'students':students,
        'staffs':staffs,
        'courses':courses,
        'branches':branches,
        'team':team
    }
    return render(request,'about.html',context=context)


def course(request):
    about = Home.objects.all()
    courses = Course.objects.all()
    context = {
        'courses':courses,
        'about':about
    }
    return render(request,'courses.html',context=context)