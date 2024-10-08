from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib import messages
from datetime import datetime
from django.utils.dateparse import parse_date
from userapp.models import *
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# register,login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password,make_password

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

import os
from django.utils import timezone

import pandas as pd

from django.core.exceptions import ValidationError

# Create your views here.

# login 

def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'registration/login.html', {'error': 'Both email and password are required.'})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'registration/login.html', {'error': 'User does not exist.'})

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('admin_home')  # Redirect to the home page
            else:
                return render(request, 'registration/login.html', {'error': 'User account is not active.'})
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid login credentials.'})
    else:
        return render(request, 'registration/login.html')
    

def dologout(request):
    logout(request)
    request.session.flush()  # Ensure the session is completely cleared
    return redirect('login') 

@login_required
def home(request):
    user = request.user  # Get the logged-in user

    staff_count = Staff.objects.all().count()
    student_count = Student.objects.all().count()
    branch_count = Branch.objects.all().count()
    course_count = Course.objects.all().count()
    pkd_students = Student.objects.filter(branch_id=1).count()
    pmna_students = Student.objects.filter(branch_id=2).count()
    student = Student.objects.all()
    branch = Branch.objects.all()
    
    # Fetching student count per branch for the bar chart
    student_branch_counts = Student.objects.values('branch_id__branch_name').annotate(student_count=Count('id')).order_by('branch_id__branch_name')

    branch_names = [item['branch_id__branch_name'] for item in student_branch_counts]
    student_counts = [item['student_count'] for item in student_branch_counts]

    student_gender_male = Student.objects.filter(gender='Male').count()
    student_gender_female = Student.objects.filter(gender='Female').count()

    context = {
        'student_count': student_count,
        'course_count': course_count,
        'branch_count': branch_count,
        'subject_count': staff_count,
        'student_gender_male': student_gender_male,
        'student_gender_female': student_gender_female,
        'student': student,
        'pkd_students': pkd_students,
        'pmna_students': pmna_students,
        'user': user,
        'branch': branch,
        'branch_names': branch_names,
        'student_counts': student_counts
    }
    return render(request, 'admin/home.html', context=context)


@login_required
def student_admission(request):
    user = request.user
    course = Course.objects.all()
    branches = Branch.objects.all()
    schemes = Scheme.objects.all()
    
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        name = request.POST.get('name')
        dob_str = request.POST.get('dob')  # Get date of birth as string
        age = request.POST.get('age')
        gaurd_name = request.POST.get('gaurd_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        education = request.POST.get('education')
        gender = request.POST.get('gender')
        other_fee = request.POST.get('other_fee', 0)
        course_id = request.POST.get('course_id')
        branch_id = request.POST.get('branch_id')
        scheme_id = request.POST.get('scheme')
        

        # Convert dob_str to date object
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

        course = Course.objects.get(id=course_id)
        branch = Branch.objects.get(id=branch_id)
        scheme = Scheme.objects.get(name=scheme_id)

        # Calculate final fee based on selected schema
        print("scheme.scheme::",scheme.scheme)
        course_fee = course.fee
        final_fee = course_fee - (course_fee * scheme.scheme)
        print("otherfeee ",final_fee)
        final_fee += float(other_fee)

        student = Student(
            profile_pic=profile_pic,
            name=name,
            email=email,
            gaurd_name=gaurd_name,
            address=address,
            education=education,
            course_id=course,
            branch_id=branch,
            scheme_id=scheme,
            gender=gender,
            phone=phone,
            dob=dob,
            age=age,
            final_fee=final_fee,
            other_fee=other_fee
        )
        student.save()

        # Sending WhatsApp message
        try:
            # Sending WhatsApp message
            client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
            message = client.messages.create(
                from_='whatsapp:+13612641426',  # Your Twilio WhatsApp number
                body=f'Hi *{name}*,\n*Welcome to Skillboard Family*🎓!!\n\nHere is your enrolled course in detail\n\n*{student.course_id.name}*\nDuration : {student.course_id.duration}\nYou will Learn : {student.course_id.description}\n\n*Fee Details*\n\nTution Fee : ₹{student.course_id.fee}\nOther Fee : ₹{student.other_fee}\nFinal Fee to pay after scheme reduction :₹{student.final_fee}\n\nIf You Have any Query\nfeel free to contact :+91 6238 627 545 \n\nHappy Learning ☺️📚📚!!\n\n*SKILLBOARD EDUCATION {student.branch_id.branch_name.upper()} 🎓*',
                to=f'whatsapp:+91{phone}'  # Phone number of the student
            )
            print("WhatsApp message SID:", message.sid)  # Log the message SID for debugging
        except Exception as e:
            print("Error sending WhatsApp message:", e)

        messages.success(request, "Student details added successfully!!")
        return redirect('student_admission')
    else:
        # Handle other request methods (e.g., GET)
        # You might want to render a template or redirect to another URL
        return render(request, 'admin/student/student_admission.html', {'course': course,'branches':branches,'schemes':schemes,'user':user})


@login_required    
def view_student(request):
    user = request.user
    if user.is_superuser:
        student = Student.objects.all()
    else:
        staff= Staff.objects.get(user = user.id)
        staff_branch = staff.branch_id
        student = Student.objects.filter(branch_id=staff_branch)
    
    context = {
        "student":student,
        "user":user
    }
    return render(request,'admin/student/view_students.html',context)


@login_required
def edit_student(request,id):
    student = Student.objects.get(id=id)
    courses = Course.objects.all()
    branches = Branch.objects.all()
    branch = student.branch_id
    course = student.course_id
    user = request.user
    context = {
        "student":student,
        "courses":courses,
        "branches":branches,
        "branch":branch,
        "course":course,
        "user":user
    }
    return render(request,'admin/student/edit_student.html',context)
@login_required
def update_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        profile_pic = request.FILES.get('profile_pic')
        name = request.POST.get('name')
        gaurd_name = request.POST.get('gaurd_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        education = request.POST.get('education')
        course_id = request.POST.get('course_id')
        branch_id = request.POST.get('branch_id')
        phone = request.POST.get('phone')
        
        course_completed = request.POST.get('course_completed') == 'on'
        certificate_issued = request.POST.get('certificate_issued') == 'on'
        examination_date = request.POST.get('examination_date')
        
        if examination_date:
            try:
                examination_date = parse_date(examination_date)
                if not examination_date:
                    raise ValidationError("Invalid date format. It must be in YYYY-MM-DD format.")
            except ValidationError as e:
                messages.error(request, e.message)
                return redirect('edit_student', student_id=student_id)
        
        student = Student.objects.get(id=student_id)
        
        fields_updated = False
        
        if name and student.name != name:
            student.name = name
            fields_updated = True
        if gaurd_name and student.gaurd_name != gaurd_name:
            student.gaurd_name = gaurd_name
            fields_updated = True
        if email and student.email != email:
            student.email = email
            fields_updated = True
        if address and student.address != address:
            student.address = address
            fields_updated = True
        if gender and student.gender != gender:
            student.gender = gender
            fields_updated = True
        if education and student.education != education:
            student.education = education
            fields_updated = True
        if phone and student.phone != phone:
            student.phone = phone
            fields_updated = True
        if student.course_completed != course_completed:
            student.course_completed = course_completed
            fields_updated = True
        if student.certificate_issued != certificate_issued:
            student.certificate_issued = certificate_issued
            fields_updated = True
        if examination_date and student.examination_date != examination_date:
            student.examination_date = examination_date
            fields_updated = True
        if profile_pic:
            student.profile_pic = profile_pic
            fields_updated = True
        
        course = Course.objects.get(id=course_id)
        if student.course_id != course:
            student.course_id = course
            fields_updated = True
        branch = Branch.objects.get(id=branch_id)
        if student.branch_id != branch:
            student.branch_id = branch
            fields_updated = True
        
        if fields_updated:
            student.save()
            
            if examination_date:
                try:
                    # Sending WhatsApp message
                    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
                    message = client.messages.create(
                        from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                        body=f'Hi *{name}*,\nYour Exams for {student.course_id.name} is Scheduled on\n\n*{student.examination_date}*\n\nIf You Have any Query\nfeel free to contact :+91 6238 627 545 \n\nBe prepared, All the best! 🌟*\n\n*SKILLBOARD EDUCATION {student.branch_id.branch_name.upper()} 🎓*',
                        to=f'whatsapp:+91{phone}'  # Phone number of the student
                    )
                    print("WhatsApp message SID:", message.sid)  # Log the message SID for debugging
                except Exception as e:
                    print("Error sending WhatsApp message:", e)
            
            messages.success(request, "Record Are Successfully Updated!")
        else:
            print("nothing updated")
        
        return redirect('view_student')
        
    return render(request, 'admin/student/edit_student.html')


@login_required
def delete_student(request,admin):
    
    student = Student.objects.get(id = admin)
    student.delete()
    messages.success(request,'Record are Successfully Deleted !')
    return redirect('view_student')


@login_required
def view_certificate(request,id):
    student = Student.objects.get(id=id)
    context = {
        'student':student
    }
    return render(request,'admin/certificate/certificate_of_completion.html',context=context)

# course
@login_required
def add_course(request):
    user = request.user
    if user:
        user = request.user
    else:
        user = None
    
    if request.method == 'POST':
        if 'course_file' in request.FILES:  # Check if a file is uploaded
            course_file = request.FILES['course_file']
            if course_file.name.endswith('.xlsx'):
                try:
                    df = pd.read_excel(course_file)  # Read Excel file
                    print("columns  :",df.columns)
                    for index, row in df.iterrows():
                        course = Course(
                            name=row['COURSE NAME'],  # Ensure column names match exactly
                            duration=row['DURATION'],
                            fee=row['FEE'],
                            photo=None,  # Adjust based on your photo handling logic
                            description=row['COURSE DECRIPTION']  # Fix typo in column name
                        )
                        course.save()
                    messages.success(request, 'Bulk Courses Successfully Added!')
                    return redirect('add_course')
                except Exception as e:
                    messages.error(request, f'Error processing file: {e}')
                    return redirect('add_course')
            else:
                messages.error(request, 'Please upload a valid Excel file.')
                return redirect('add_course')
        
        # Process single course addition as before if no file uploaded
        course_name = request.POST.get('course_name')
        course_duration = request.POST.get('course_duration')
        course_fee = request.POST.get('course_fee')
        photo = request.FILES.get('photo')
        description = request.POST.get('course_description')
        course = Course(
            name=course_name,
            duration=course_duration,
            fee=course_fee,
            photo=photo,
            description=description
        )
        course.save()
        messages.success(request, 'Course Successfully Created!')
        return redirect('add_course')
    
    return render(request, 'admin/course/add_course.html', {'user': user})


@login_required
def view_course(request):
    user = request.user
    course = Course.objects.all()
    context = {
        'course':course,
        "user":user
    }
    return render(request,'admin/course/view_course.html',context)


@login_required
def edit_course(request,id):
    course = Course.objects.get(id = id)
    user = request.user
    context = {
        'course':course,
        "user":user
    }
    return render(request,'admin/course/edit_course.html',context)


@login_required
def update_course(request):
    if request.method == "POST":
       name  = request.POST.get('course_name')
       description  = request.POST.get('course_description')
       photo  = request.FILES.get('photo')
       duration = request.POST.get('course_duration')
       fee = request.POST.get('course_fee')
       course_id = request.POST.get('course_id')
       
       course = Course.objects.get(id = course_id)
       course.duration = duration
       course.fee = fee
       course.name = name
       course.photo = photo
       course.description = description
       course.save()
       messages.success(request,'Course updated successfully !')
       return redirect('view_course')
    return render(request,'admin/course/edit_course.html')


@login_required
def delete_course(request, id):
    course = get_object_or_404(Course, id=id) 
    try:
        course.delete()
        messages.success(request, 'Course has been successfully deleted!')
    except Exception as e:
        messages.error(request, f'Error deleting course: {str(e)}')
    
    return redirect('view_course')

# Fee payment Section 
# .......................

@login_required
def fee_payment(request,id):
    user = request.user
    student = Student.objects.get(id=id)
    final_fee = student.final_fee
    payments = Payment.objects.filter(student=id)
    
    context = {
        'student':student,
        'final_fee':final_fee,
        'payments':payments,
        'user':user
    }
    
    # pay
    if request.method == "POST":
        payed_amount  = request.POST.get('pay')
        payment_option_id = request.POST.get('payment_option')
        phone = request.POST.get('phone')
        
        student = Student.objects.get(id = id)
        student.final_fee = student.final_fee - float(payed_amount)
        student.save()
        payment = Payment(
            student = student,
            pay_option = payment_option_id,
            amount = payed_amount,
            phone_number = phone
        )
        payment.save()
        if payment:
            try:
                client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
                message = client.messages.create(
                    from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                    body=f'Hi *{payment.student.name}*,\nYour payment of *₹{payment.amount}* has been successfully processed!!. please collect your reciept.\n\nBalance amount to Pay : *₹{payment.student.final_fee}*\n\nIf You Have any Query\nfeel free to contact :+91 6238 627 545 \n\nThank You! 🌟\n\n*SKILLBOARD EDUCATION {payment.student.branch_id.branch_name.upper()} 🎓*',
                    to=f'whatsapp:+91{payment.student.phone}'  # Phone number of the student
                )
                print("WhatsApp message SID:", message.sid)  # Log the message SID for debugging
            except Exception as e:
                print("Error sending WhatsApp message:", e)
        
        messages.success(request, "Payment Success !!")
        return redirect('fee_payment',id=student.id)
      
    return render(request,'admin/payment/fee_payment.html',context=context)


@login_required
def view_reciept(request,id):
    user = request.user
    payment = Payment.objects.get(id=id)
    student_id =payment.student.id
    branch_code = payment.student.branch_id.branch_code
    context = {
        'payment':payment,
        'student_id':student_id,
        'branch_code':branch_code,
        'user':user
    }
    return render(request,'admin/reciept/reciept.html',context=context)


@login_required
def payed_list(request):
    user = request.user
    if user.is_superuser:
        payments = Payment.objects.all()
    
    else:
        staff = Staff.objects.get(user=user)  # Assuming staff is related to the branch
        staff_branch = staff.branch_id
        # Filter students based on the staff's branch
        students = Student.objects.filter(branch_id=staff_branch)

        # Filter payments based on the students belonging to the staff's branch
        payments = Payment.objects.filter(student__in=students)
    id = []
    student_id = []
    name = []
    payed_amount = []
    way_of_pay = []
    phone = []
    payed_date = []
    branch_code = []
    balance = []
    branch = []
    for i in payments:
        id.append(i.id)
        student_id.append(i.student.id)
        branch_code.append(i.student.branch_id.branch_code)
        name.append(i.student.name)
        payed_amount.append(i.amount)
        way_of_pay.append(i.pay_option)
        phone.append(i.phone_number)
        payed_date.append(i.created_at)
        balance.append(i.student.final_fee)
        branch.append(i.student.branch_id.branch_name)
        
    payments = zip(id,student_id,name,payed_amount,way_of_pay,phone,payed_date,branch_code,balance,branch)
    context = {
        'payments':payments,
        'user':user
    }
    return render(request,'admin/payment/payed_list.html',context=context)



@login_required
def add_branch(request):
    branches = Branch.objects.all()
    user = request.user
    if request.method == "POST":
        name  = request.POST.get('branch_name')
        code = request.POST.get('branch_code')
        photo = request.FILES.get('branch_photo')
        address1  = request.POST.get('address1')
        address2 = request.POST.get('address2')
        address3 = request.POST.get('address3')
        contact1 = request.POST.get('contact1')
        contact2 = request.POST.get('contact2')
        mail = request.POST.get('mail')
        fb = request.POST.get('fb')
        insta = request.POST.get('insta')
        linkdn = request.POST.get('linkdn')
        photo = request.FILES.get('branch_photo')
        gmap = request.POST.get('gmap')
        branch = Branch(branch_name=name,branch_code=code,photo=photo,address1=address1,address2=address2,address3=address3,mail=mail,contact_no1=contact1,contact_no2=contact2,facebook=fb,instagram=insta,linkedin=linkdn,gmap=gmap)
        branch.save()
        messages.success(request, "Branch Added Successfully !!",{'user':request.user})
        return redirect('add_branch')
    context = {
        'branches':branches,
        'user':user
    }
    return render(request,'admin/branch/add_branch.html',context=context)

@login_required
def update_branch(request,id):
    branch = Branch.objects.get(id=id)
    user = request.user
    if request.method == "POST":
        name  = request.POST.get('branch_name')
        code = request.POST.get('branch_code')
        photo = request.FILES.get('branch_photo')
        address1  = request.POST.get('address1')
        address2 = request.POST.get('address2')
        address3 = request.POST.get('address3')
        contact1 = request.POST.get('contact1')
        contact2 = request.POST.get('contact2')
        gmap = request.POST.get('gmap')
        mail = request.POST.get('mail')
        fb = request.POST.get('fb')
        insta = request.POST.get('insta')
        linkdn = request.POST.get('linkdn')
        photo = request.FILES.get('branch_photo')
        
        branch.branch_name=name
        branch.branch_code=code
        branch.photo=photo
        branch.address1=address1
        branch.address2=address2
        branch.address3=address3
        branch.mail=mail
        branch.contact_no1=contact1
        branch.contact_no2=contact2
        branch.facebook=fb
        branch.instagram=insta
        branch.linkedin=linkdn
        branch.gmap = gmap
        branch.save()
        messages.success(request, "Branch Updated Successfully !!",{'user':request.user})
        return redirect('add_branch')
    context = {
        'branch':branch,
        'user':user
    }
    return render(request,'admin/branch/edit_branch.html',context=context)


@login_required
def delete_branch(request,id):
    branch = Branch.objects.get(id = id)
    branch.delete()
    messages.success(request,'Branch Deleted !!')
    return redirect('add_branch')


@login_required
def view_contacts(request):
    user = request.user
    user_dtl = contacted_user.objects.all()
    context = {
        'user':user,
        'user_dtl':user_dtl
    }
    return render(request,'admin/contact/view_contact.html',context)

@login_required
def contact_followup(request,id):
    user = request.user
    courses = Course.objects.all()
    cuser = contacted_user.objects.get(id=id)
    context = {
        'user':user,
        'cuser':cuser,
        'courses':courses
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')  
        phone = request.POST.get('phone')  
        course_id = request.POST.get('course_id')
        message = request.POST.get('message')
        remarks = request.POST.get('remarks')
        
        # Save form data to the user model
        course = Course.objects.get(id=course_id)
        cuser.name=name
        cuser.email=email
        cuser.phone=phone
        cuser.course=course
        cuser.message=message
        cuser.remarks=remarks
        cuser.is_follow = True
        cuser.save()
        
        messages.success(request,"follow up successfully!!")
        return redirect('view_contacts')
    else:
        return render(request,'admin/contact/contact_followup.html',context)
    

@login_required
def delete_contact(request,id):
    contact = contacted_user.objects.get(id = id)
    contact.delete()
    messages.success(request,'Contact Deleted !!')
    return redirect('view_contacts')
    


# addstaff
@login_required
def add_staff(request):
    user = request.user
    department = Department.objects.all()
    branches = Branch.objects.all()
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        name = request.POST.get('name')
        dob_str = request.POST.get('dob') 
        age = request.POST.get('age')
        gaurd_name = request.POST.get('gaurd_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        department_id = request.POST.get('department_id')
        branch_id = request.POST.get('branch_id')
        password_in = request.POST.get('password')
        
        

        # Convert dob_str to date object
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

        department = Department.objects.get(id=department_id)
        branch = Branch.objects.get(id=branch_id)
        
        username = name.replace(' ', '')
        
        # Check if the user already exists
        existing_user = User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()
        if existing_user:
            messages.error(request, "User with this username or email already exists.")
            return redirect('add_staff')
        
        if password_in == '' or password_in is None:
            password = name
            access_to_web = False
        else:
            password = password_in
            access_to_web = True

        # Create the User object
        user = User.objects.create_user(username=username, email=email, password=password)
        
        
        user.is_staff = True
        user.is_superuser = False
        user.save()
            
        staff = Staff(
            profile_pic=profile_pic,
            name=name,
            gaurd_name=gaurd_name,
            address=address,
            department=department,
            branch_id=branch,
            gender=gender,
            phone=phone,
            dob=dob,
            age=age,
            user=user,
            access_to_web=access_to_web
        )
        staff.save()

        messages.success(request, "staff details added successfully!!")
        return redirect('add_staff')
    else:
        return render(request, 'admin/staff/add_staff.html', {'department': department,'branches':branches,'user':user})
    
    
@login_required
def view_staff(request):
    user = request.user
    staff = Staff.objects.all()
    
    context = {
        "staff":staff,
        'user':user
    }
    return render(request,'admin/staff/view_staff.html',context)


@login_required
def edit_staff(request,id):
    user = request.user
    staff = Staff.objects.get(id=id)
    departments = Department.objects.all()
    branches = Branch.objects.all()
    context = {
        "staff":staff,
        "departments":departments,
        "branches":branches,
        'user':user
    }
    return render(request,'admin/staff/edit_staff.html',context)


@login_required
def update_staff(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        profile_pic = request.FILES.get('profile_pic')
        name = request.POST.get('name')
        gaurd_name = request.POST.get('gaurd_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        department_id = request.POST.get('department_id')
        phone = request.POST.get('phone')
        password_in = request.POST.get('password')
        print("Password:",staff_id)

        staff = Staff.objects.get(id = staff_id)
        department = Department.objects.get(id=department_id)
        user = User.objects.get(id=staff.user.id)
        print("staff.user.id",staff.user.id)
        user.email = email
        user.is_staff = True
        user.is_superuser = False
        
        if password_in is None or password_in == '':
            password = name
            staff.user.password = password
        
        staff.name = name
        staff.gaurd_name = gaurd_name
        staff.address = address
        staff.gender = gender
        staff.phone = phone
        staff.user.email = email
        staff.department = department
        staff.user = user
        staff.user.password = make_password(password_in)

        if profile_pic:
            staff.profile_pic = profile_pic
        staff.save()
        staff.user.save()
        print(staff.user.password)
        
        messages.success(request,"Record Are Successfully Updated !")
        return redirect('view_staff')
        
    return render(request,'admin/staff/edit_staff.html')


@login_required
def delete_staff(request,admin):
    staff = Staff.objects.get(id = admin)
    staff.delete()
    messages.success(request,'Record are Successfully Deleted !')
    return redirect('view_staff')


# department
#..........................................................................

@login_required
def add_department(request):
    user = request.user
    if request.method == 'POST':
        department_name = request.POST.get('department_name')
        department = Department(
            name = department_name
        )
        department.save()
        messages.success(request,'department Addedd Successfully !')
        return redirect('add_department')
    return render(request,'admin/department/add_department.html',{'user':user})


@login_required
def view_department(request):
    user = request.user
    department = Department.objects.all()
    context = {
        'department':department,
        'user':user
    }
    return render(request,'admin/department/view_department.html',context)


@login_required
def edit_department(request,id):
    user = request.user
    department = Department.objects.get(id = id)

    context = {
        'department':department,
        'user':user
    }
    return render(request,'admin/department/edit_department.html',context)


@login_required
def update_department(request):
    if request.method == "POST":
       name  = request.POST.get('name')
       department_id = request.POST.get('department_id')
       
       department = Department.objects.get(id = department_id)
       department.name = name
       department.save()
       messages.success(request,'department updated successfully !')
       return redirect('view_department')
    return render(request,'admin/department/edit_department.html')


@login_required
def delete_department(request,id):
    department = Department.objects.get(id = id)
    department.delete()
    messages.success(request,'department Successfully Deleted !')
    return redirect('view_department')

# scheme
@login_required
def scheme(request):
    schemes = Scheme.objects.all()
    user = request.user
    scheme_id = []
    scheme_names = []
    scheme_amount = []
    scheme_created = []
    for i in schemes:
        scheme_id.append(i.id)
        scheme_names.append(i.name)
        scheme_amount.append(i.scheme*100)
        scheme_created.append(i.created_at)
    display_scheme = zip(scheme_id,scheme_names,scheme_amount,scheme_created)
    if request.method == "POST":
        scheme_name  = request.POST.get('scheme_name')
        scheme = request.POST.get('scheme')
        photo = request.FILES.get('scheme_photo')
        schemed = float(scheme)*(1/100)
        schem = Scheme(name=scheme_name,scheme=schemed,photo=photo)
        schem.save()
        messages.success(request, "Scheme Added Successfully !!",{'user':user})
        return redirect('scheme')
    context = {
        'schemes':schemes,
        'user':user,
        'display_scheme':display_scheme
    }
    return render(request,'admin/scheme/add_scheme.html',context=context)

@login_required
def edit_scheme(request,id):
    schemes = Scheme.objects.get(id=id)
    user = request.user
    if request.method == "POST":
        scheme_name  = request.POST.get('scheme_name')
        scheme = request.POST.get('scheme')
        photo = request.FILES.get('scheme_photo')
        schemed = float(scheme)*(1/100)
        schemes.name=scheme_name
        schemes.scheme=schemed
        schemes.photo=photo
        schemes.save()
        messages.success(request, "Scheme Updated Successfully !!",{'user':user})
        return redirect('scheme')
    context = {
        'schemes':schemes,
        'user':user
    }
    return render(request,'admin/scheme/edit_scheme.html',context=context)

@login_required
def delete_scheme(request,id):
    try:
        scheme = Scheme.objects.get(id = id)
        scheme.delete()
        messages.success(request,'Scheme Deleted !!')
    except Exception:
        messages.error(request,'You Cant Delete this scheme because this scheme is used by students, please add new scheme and change scheme in student edit section!!')
    
    return redirect('scheme')


# testimonals
@login_required
def testimonals(request):
    tests = Testimonal.objects.all()
    user = request.user
    if request.method == "POST":
        name  = request.POST.get('name')
        designation = request.POST.get('designation')
        photo = request.FILES.get('photo')
        message = request.POST.get('message')
        test = Testimonal(name=name,designation=designation,photo=photo,message=message)
        test.save()
        messages.success(request, "Testimonal Added Successfully !!")
        return redirect('test')
    context = {
        'tests':tests,
        'user':user
    }
    return render(request,'admin/testimonal/testimonal.html',context=context)


@login_required
def delete_testimonal(request,id):
    test = Testimonal.objects.get(id = id)
    test.delete()
    messages.success(request,'testimonall Deleted !!')
    return redirect('test')


# bg image

@login_required
def add_bg_image(request):
    bgs = Bgimages.objects.all()
    context = {
        'bgs':bgs
    }
    if request.method == 'POST':
        image = request.FILES.get('image')
        bgimages = Bgimages(bgimage = image)
        bgimages.save()
        messages.success(request,"Background image added successfully!!")
        return redirect('add_bg_image')
    return render(request,'admin/home/bg_image.html',context=context)


@login_required
def delete_bg_image(request,id):
    bg = Bgimages.objects.get(id = id)
    bg.delete()
    messages.success(request,'Image Deleted !!')
    return redirect('add_bg_image')

@login_required
def home_titles(request):
    home_dtl = Home.objects.all()
    about_instance, created = About.objects.get_or_create(pk=1)
    print("vvvv,",about_instance.about,"\n",about_instance.mission,"\n",about_instance.vision)
    if request.method == 'POST':
        if 'add_qoute' in request.POST:
            qoute1 = request.POST.get('qoute1')
            qoute2 = request.POST.get('qoute2')
            by = request.POST.get('by')
            home = Home(qoute1=qoute1,qoute2=qoute2,by=by)
            home.save()
            messages.success(request, "Qoute Added successfully!")
            return redirect('home_titles')
        
        elif 'about_submit' in request.POST:
            aboutin = request.POST.get('about')
            print("in:::",aboutin)
            about_instance.about=aboutin
            about_instance.save()
            print("about_instance.about",about_instance.about)
            messages.success(request, "About Changed successfully!")
            return redirect('home_titles')
        
        elif 'vision_submit' in request.POST:
            vision = request.POST.get('vision')
            print("in:::", vision)
            about_instance.vision = vision
            about_instance.save()
            messages.success(request, "Vision Changed successfully!")
            return redirect('home_titles')
        
        elif 'mission_submit' in request.POST:
            mission = request.POST.get('mission')
            print("in:::",mission)
            about_instance.mission=mission
            about_instance.save()
            messages.success(request, "Mission Changed successfully!")
            return redirect('home_titles')
    
    context = {
        "home_dtl":home_dtl,
        "about":about_instance
    }
    
    return render(request, 'admin/home/home_page_edit.html',context=context)

@login_required
def delete_home_qoute(request,id):
    home = Home.objects.get(id = id)
    home.delete()
    messages.success(request,'Qoute in Home deleted!!')
    return redirect('home_titles')


# Logos 
@login_required
def add_logo(request):
    log = AffLogo.objects.all()
    context = {
        'log':log
    }
    if request.method == 'POST':
        image = request.FILES.get('image')
        logo = AffLogo(logo = image)
        logo.save()
        messages.success(request,"New logo added successfully!!")
        return redirect('logo_index')
    return render(request,'admin/home/logos.html',context=context)


@login_required
def delete_logo(request,id):
    logo = AffLogo.objects.get(id = id)
    logo.delete()
    messages.success(request,'Logo deleted!!')
    return redirect('logo_index')


# Enquiry

@login_required
def add_enquiry(request):
    enq = Enquiry.objects.filter(created_by=request.user)
    course = Course.objects.all()
    
    if request.method == 'POST':
        if 'enquiry_file' in request.FILES:  # Check if a file is uploaded
            enquiry_file = request.FILES['enquiry_file']
            if enquiry_file.name.endswith('.xlsx'):
                try:
                    df = pd.read_excel(enquiry_file, header=0)  # Read Excel file
                    for index, row in df.iterrows():
                        name = row['NAME']
                        phone = row['PHONE']
                        # Set the created_by field to the current user
                        enquiry = Enquiry(name=name, phone=phone, created_by=request.user)
                        enquiry.save()
                    messages.success(request, 'Bulk Enquiries Successfully Added!')
                    return redirect('enquiry')
                except Exception as e:
                    messages.error(request, f'Error processing file: {e}')
                    return redirect('enquiry')
            else:
                messages.error(request, 'Please upload a valid Excel file.')
                return redirect('enquiry')
        
        # Process single enquiry addition as before if no file uploaded
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        course_id = request.POST.get('course_id')
        selected_course = Course.objects.get(id=course_id)
        
        # Set the created_by field to the current user
        enquiry = Enquiry(name=name, phone=phone, remarks=remarks, course=selected_course, created_by=request.user)
        enquiry.save()
        messages.success(request, 'Enquiry Added successfully!!')
        return redirect('enquiry')

    context = {
        'enq': enq,
        'course': course
    }
    
    return render(request, 'staff/enquiry_form.html', context=context)

@login_required
def edit_enquiry(request, id):
    courses = Course.objects.all()
    enq = get_object_or_404(Enquiry, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        course_id = request.POST.get('course_id')
        selected_course = get_object_or_404(Course, id=course_id)

        enq.name = name
        enq.phone = phone
        enq.remarks = remarks
        enq.course = selected_course

        if 'update_enquiry' in request.POST:
            enq.save()
            messages.success(request, "Enquiry Updated Successfully!!")
            return redirect('enquiry')

        elif 'send_message' in request.POST:
            try:
                # Send course details to the phone number using Twilio
                send_course_details(phone, selected_course,name)
                messages.success(request, "Message sent successfully!")
            except Exception as e:
                messages.error(request, f"Failed to send message: {e}")
            return redirect('edit-enquiry', id=id)

    context = {
        'enq': enq,
        'courses': courses
    }
    return render(request, 'staff/edit_enquiry.html', context=context)

def send_course_details(phone, course,name):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=f"Hi *{name}*,\n\n*Greetings from Skillboard Education*\n\n\nHere is Your Course Details:\n\nCourse Name: *{course.name}*\n\nWe will cover: \n{course.description}\n\nDuration : {course.duration}\n\nIf You Have any Query\nfeel free to contact :+91 6238 627 545 \n\nHappy Learning ☺️📚📚!!\n\n*SKILLBOARD EDUCATION* 🎓",
            from_='whatsapp:+14155238886',  # Your Twilio number
            to=f"whatsapp:+91{phone}"
        )
    except TwilioRestException as e:
        raise Exception(f"Twilio error: {e.msg}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")
    

@login_required
def delete_enquiry(request,id):
    enq = Enquiry.objects.get(id=id)
    enq.delete()
    messages.success(request,'Enquiry Deleted!!')
    return redirect('enquiry')


@login_required
def enq_to_admission(request,id):
    enq = Enquiry.objects.get(id=id)
    course = Course.objects.all()
    context = {
        'enq':enq,
        'course':course
    }
    return render(request,'admin/student/student_admission.html',context=context)

@login_required
def add_image_gallery(request):
    imgs = ImgGallary.objects.all()
    context = {
        'imgs':imgs
    }
    if request.method == 'POST':
        image = request.FILES.get('image')
        bgimages = ImgGallary(image = image)
        bgimages.save()
        messages.success(request,"Image added successfully!!")
        return redirect('img_gallery')
    return render(request,'admin/home/image_gallery.html',context=context)

@login_required
def delete_image(request,id):
    img = ImgGallary.objects.get(id = id)
    img.delete()
    messages.success(request,'Image Deleted !!')
    return redirect('img_gallery')

####################### placements ###########
# scheme
@login_required
def placement(request):
    placement = Placement.objects.all()
    user = request.user
    p_id = []
    company_name = []
    place = []
    position = []
    description = []
    placement_created = []
    for i in placement:
        p_id.append(i.id)
        company_name.append(i.company_name)
        place.append(i.place)
        position.append(i.position)
        description.append(i.description)
        placement_created.append(i.created_at)
    display_placement = zip(p_id,company_name,place,position,description,placement_created)
    if request.method == "POST":
        company_name  = request.POST.get('company_name')
        place = request.POST.get('place')
        position  = request.POST.get('position')
        description = request.POST.get('description')
        placement = Placement(company_name=company_name,place=place,position=position,description=description)
        placement.save()
        messages.success(request, "Vacancy Added Successfully !!",{'user':user})
        return redirect('placement')
    context = {
        'placements':placement,
        'user':user,
        'display_placement':display_placement
    }
    return render(request,'admin/placements/add_placements.html',context=context)


@login_required
def delete_placement(request,id):
    try:
        placement = Placement.objects.get(id = id)
        placement.delete()
        messages.success(request,'Vacancy Deleted !!')
    except Exception:
        messages.error(request,'You Cant Delete this scheme because this scheme is used by students, please add new scheme and change scheme in student edit section!!')
    
    return redirect('placement')
