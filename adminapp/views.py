from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib import messages
from datetime import datetime
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
import os
from django.utils import timezone

import pandas as pd

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

        if not check_password(password, user.password):
            print("pass1",password,"user.password",user.password)
            return render(request, 'registration/login.html', {'error': 'Invalid password.'})

        if not user.is_active:
            return render(request, 'registration/login.html', {'error': 'User account is not active.'})

        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            print("pass1",password,"user.password",user.password)
            return redirect('admin_home')
        else:
            return render(request, 'registration/login.html', {'error': 'Unable to log in.'})
    else:
        return render(request, 'registration/login.html')
    

def dologout(request):
    logout(request)
    return redirect('login') 


def home(request):
    try:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
    except KeyError:
        # User_id is not found in session
        return render(request, 'registration/login.html', {'error': 'User ID not found in session. Please log in.'})
    except User.DoesNotExist:
        # User with the provided ID does not exist
        return render(request, 'registration/login.html', {'error': 'User does not exist.'})
    
    # Proceed with other logic if the user is found
    student_count = Student.objects.all().count()
    branch_count = Branch.objects.all().count()
    course_count = Course.objects.all().count()
    pkd_students = Student.objects.filter(branch_id=1).count()
    pmna_students = Student.objects.filter(branch_id=2).count()
    student = Student.objects.all()

    student_gender_male = Student.objects.filter(gender='Male').count()
    student_gender_female = Student.objects.filter(gender='Female').count()

    context = {
        'student_count': student_count,
        'course_count': course_count,
        'subject_count': branch_count,
        'student_gender_male': student_gender_male,
        'student_gender_female': student_gender_female,
        'student': student,
        'pkd_students': pkd_students,
        'pmna_students': pmna_students,
        'user': user
    }
    return render(request, 'admin/home.html', context=context)


@login_required
def student_admission(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
        return render(request, 'admin/student_admission.html', {'course': course,'branches':branches,'schemes':schemes,'user':user})


@login_required    
def view_student(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    student = Student.objects.all()
    
    context = {
        "student":student,
        "user":user
    }
    return render(request,'admin/view_students.html',context)


@login_required
def edit_student(request,id):
    student = Student.objects.get(id=id)
    courses = Course.objects.all()
    branches = Branch.objects.all()
    branch = student.branch_id
    course = student.course_id
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    context = {
        "student":student,
        "courses":courses,
        "branches":branches,
        "branch":branch,
        "course":course,
        "user":user
    }
    return render(request,'admin/edit_student.html',context)


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
        course_id = request.POST.get('course_id')
        phone = request.POST.get('phone')
        
        course_completed = request.POST.get('course_completed')
        certificate_issued = request.POST.get('certificate_issued')
        examination_date = request.POST.get('examination_date')
        
        if course_completed == 'on':
            course_completed = True
        else:
            course_completed = False
            
        if certificate_issued == 'on':
            certificate_issued = True
        else:
            certificate_issued = False


        student = Student.objects.get(id = student_id)
        student.name = name
        student.gaurd_name = gaurd_name
        student.email = email
        student.address = address
        student.gender = gender
        student.phone = phone
        
        student.course_completed = course_completed
        student.certificate_issued = certificate_issued
        student.examination_date = examination_date

        if profile_pic:
            student.profile_pic = profile_pic
        course = Course.objects.get(id=course_id)
        student.course_id = course
        student.save()
        
        if student.examination_date:
            try:
                # Sending WhatsApp message
                client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
            
                message = client.messages.create(
                    from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                    body = f'Hi *{name}*,\nYour Exams for {student.course_id.name} is Scheduled on\n\n*{student.examination_date}*\n\nIf You Have any Query\nfeel free to contact :+91 6238 627 545 \n\nBe prepared, All the best! 🌟*\n\n*SKILLBOARD EDUCATION {student.branch_id.branch_name.upper()} 🎓*',
                    to=f'whatsapp:+91{phone}'  # Phone number of the student
                )
                print("WhatsApp message SID:", message.sid)  # Log the message SID for debugging
            except Exception as e:
                print("Error sending WhatsApp message:", e)
            
        messages.success(request,"Record Are Successfully Updated !")
        return redirect('view_student')
        
    return render(request,'admin/edit_student.html')


@login_required
def delete_student(request,admin):
    
    student = Student.objects.get(id = admin)
    student.delete()
    messages.success(request,'Record are Successfully Deleted !')
    return redirect('view_student')


# course
@login_required
def add_course(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = User.objects.get(id=user_id)
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
    
    return render(request, 'admin/add_course.html', {'user': user})


@login_required
def view_course(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    course = Course.objects.all()
    context = {
        'course':course,
        "user":user
    }
    return render(request,'admin/view_course.html',context)


@login_required
def edit_course(request,id):
    course = Course.objects.get(id = id)
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    context = {
        'course':course,
        "user":user
    }
    return render(request,'admin/edit_course.html',context)


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
    return render(request,'admin/edit_course.html')


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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
      
    return render(request,'admin/fee_payment.html',context=context)


@login_required
def view_reciept(request,id):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    payments = Payment.objects.all()
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
    return render(request,'admin/payed_list.html',context=context)



@login_required
def add_branch(request):
    branches = Branch.objects.all()
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        name  = request.POST.get('branch_name')
        code = request.POST.get('branch_code')
        photo = request.FILES.get('branch_photo')
        branch = Branch(branch_name=name,branch_code=code,photo=photo)
        branch.save()
        messages.success(request, "Branch Added Successfully !!",{'user':request.session['user_id']})
        return redirect('add_branch')
    context = {
        'branches':branches,
        'user':user
    }
    return render(request,'admin/add_branch.html',context=context)


@login_required
def delete_branch(request,id):
    branch = Branch.objects.get(id = id)
    branch.delete()
    messages.success(request,'Branch Deleted !!')
    return redirect('add_branch')


@login_required
def view_contacts(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    user_dtl = contacted_user.objects.all()
    context = {
        'user':user,
        'user_dtl':user_dtl
    }
    return render(request,'admin/contact/view_contact.html',context)

@login_required
def contact_followup(request,id):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    staff = Staff.objects.all()
    
    context = {
        "staff":staff,
        'user':user
    }
    return render(request,'admin/staff/view_staff.html',context)


@login_required
def edit_staff(request,id):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    print("user  :",user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    department = Department.objects.all()
    context = {
        'department':department,
        'user':user
    }
    return render(request,'admin/department/view_department.html',context)


@login_required
def edit_department(request,id):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
        messages.success(request, "Scheme Added Successfully !!",{'user':request.session['user_id']})
        return redirect('scheme')
    context = {
        'schemes':schemes,
        'user':user,
        'display_scheme':display_scheme
    }
    return render(request,'admin/add_scheme.html',context=context)

@login_required
def delete_scheme(request,id):
    try:
        scheme = Scheme.objects.get(id = id)
        scheme.delete()
        messages.success(request,'Scheme Deleted !!')
    except Exception:
        messages.error(request,'You Cant Delete this scheme because this scheme is used by students, please add new scheme and change scheme in student edit section!!')
    
    return redirect('scheme')

@login_required
def testimonals(request):
    tests = Testimonal.objects.all()
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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

# Enquiry

@login_required
def add_enquiry(request):
    enq = Enquiry.objects.all()
    course = Course.objects.all()
    
    if request.method == 'POST':
        if 'enquiry_file' in request.FILES:  # Check if a file is uploaded
            enquiry_file = request.FILES['enquiry_file']
            if enquiry_file.name.endswith('.xlsx'):
                try:
                    df = pd.read_excel(enquiry_file,header=0)  # Read Excel file
                    print("columns  :",df.columns)
                    for index, row in df.iterrows():
                        name = row['NAME']
                        phone = row['PHONE']
                        enquiry = Enquiry(name=name, phone=phone)
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
        
        enquiry = Enquiry(name=name, phone=phone, remarks=remarks, course=selected_course)
        enquiry.save()
        messages.success(request, 'Enquiry Added successfully!!')
        return redirect('enquiry')

    context = {
        'enq': enq,
        'course': course
    }
    
    return render(request, 'staff/enquiry_form.html', context=context)

@login_required
def edit_enquiry(request,id):
    courses = Course.objects.all()
    enq = Enquiry.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        remarks = request.POST.get('remarks')
        course = request.POST.get('course_id')
        selected_course = Course.objects.get(id=course)
        
        enq.name = name
        enq.phone = phone
        enq.remarks = remarks
        enq.course = selected_course
        enq.save()
        messages.success(request,"Enquiry Updated Successfully!!")
        return redirect('enquiry')
    context = {
        'enq':enq,
        'courses':courses
    }
    return render(request,'staff/edit_enquiry.html',context=context)

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
    return render(request,'admin/student_admission.html',context=context)