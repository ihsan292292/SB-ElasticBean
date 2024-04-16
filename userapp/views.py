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
    # home = Home.objects.get(id=1)
    context = {
        'courses':courses,
        'staffs':staffs,
        'bgs':bgs,
        # 'home':home
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
        
        messages.success(request,"message sent successfully!!")
        return redirect('contact')
    else:
        return render(request,'contact.html',context=context)
    
def about(request):
    students = Student.objects.all().count()
    staffs = Staff.objects.all().count()
    courses = Course.objects.all().count()
    branches = Branch.objects.all().count()
    testimonials = Testimonal.objects.all()
    about = Home.objects.all()
    context = {
        'testimonials':testimonials,
        'about':about,
        'students':students,
        'staffs':staffs,
        'courses':courses,
        'branches':branches
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


def add_bg_image(request):
    bgs = Bgimages.objects.all()
    context = {
        'bgs':bgs
    }
    if request.method == 'POST':
        image = request.FILES.get('image')
        print("imagesssss",image)
        bgimages = Bgimages(bgimage = image)
        bgimages.save()
        messages.success(request,"Background image added successfully!!")
        return redirect('add_bg_image')
    return render(request,'admin/home/bg_image.html',context=context)


def delete_bg_image(request,id):
    bg = Bgimages.objects.get(id = id)
    bg.delete()
    messages.success(request,'Image Deleted !!')
    return redirect('add_bg_image')


def home_titles(request):
    home = Home.objects.get(id=1)
    context = {
        'home':home
    }
    # home edit
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        about = request.POST.get('about')
        home.title = title
        home.subtitle = subtitle
        home.about = about
        home.save()
        messages.success(request,"successfully changed!!")
        return redirect('home_titles')
    return render(request,'admin/home/home_page_edit.html',context=context)
        