from django.shortcuts import render,redirect
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

        if not user.check_password(password):
            return render(request, 'registration/login.html', {'error': 'Invalid password.'})

        if not user.is_active:
            return render(request, 'registration/login.html', {'error': 'User account is not active.'})

        # Authenticating the user
        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            request.session['user_id'] = user.id
            login(request, user)
            return redirect('admin_home')
        else:
            return render(request, 'registration/login.html', {'error': 'Unable to log in.'})
    else:
        return render(request, 'registration/login.html')
    

def dologout(request):
    logout(request)
    return redirect('login') 


def home(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    student_count = Student.objects.all().count()
    branch_count = Branch.objects.all().count()
    course_count = Course.objects.all().count()
    pkd_students = Student.objects.filter(branch_id=1).count()
    pmna_students = Student.objects.filter(branch_id=2).count()
    student = Student.objects.all()

    student_gender_male = Student.objects.filter(gender = 'Male').count()
    student_gender_female = Student.objects.filter(gender = 'Female').count()


    context = {
        'student_count':student_count,
        'course_count':course_count,
        'subject_count':branch_count,
        'student_gender_male':student_gender_male,
        'student_gender_female':student_gender_female,
        'student':student,
        'pkd_students':pkd_students,
        'pmna_students':pmna_students,
        'user':user
    }
    return render(request,'admin/home.html',context=context)


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
        course_id = request.POST.get('course_id')
        branch_id = request.POST.get('branch_id')
        scheme_id = request.POST.get('scheme')
        print("iddddd",scheme_id)

        # Convert dob_str to date object
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

        course = Course.objects.get(id=course_id)
        branch = Branch.objects.get(id=branch_id)
        scheme = Scheme.objects.get(name=scheme_id)

        # Calculate final fee based on selected schema
        course_fee = course.fee
        final_fee = course_fee * scheme.scheme
        

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
            final_fee=final_fee 
        )
        student.save()

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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    context = {
        "student":student,
        "courses":courses,
        "branches":branches,
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


        student = Student.objects.get(id = student_id)
        student.name = name
        student.gaurd_name = gaurd_name
        student.email = email
        student.address = address
        student.gender = gender
        student.phone = phone

        if profile_pic:
            student.profile_pic = profile_pic
        course = Course.objects.get(id=course_id)
        student.course_id = course
        student.save()
        
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_duration = request.POST.get('course_duration')
        course_fee = request.POST.get('course_fee')
        photo = request.FILES.get('photo')
        description = request.POST.get('course_description')
        course = Course(
            name = course_name,
            duration = course_duration,
            fee = course_fee,
            photo = photo,
            description = description
        )
        course.save()
        messages.success(request,'Course Are Successfully Created !')
        return redirect('add_course')
    return render(request,'admin/add_course.html',{'user':user})


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
def delete_course(request,id):
    course = Course.objects.get(id = id)
    course.delete()
    messages.success(request,'Course are Successfully Deleted !')
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
def generate_pdf(request, id):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    payment = Payment.objects.get(id=id)
    student_id = payment.student.id
    branch_code = payment.student.branch_id.branch_code
    context = {
        'payment': payment,
        'student_id': student_id,
        'branch_code': branch_code,
        'user': user
    }

    # Render the HTML template to a string
    receipt_html = render_to_string('admin/view_reciept.html', context=context)

    # Generate the PDF file
    pdf = pdfkit.from_string(str(receipt_html), options={"enable-local-file-access": ""})
    

    # Return the PDF file as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    return response


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
        
    payments = zip(id,student_id,name,payed_amount,way_of_pay,phone,payed_date,branch_code,balance)
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
    user = contacted_user.objects.all()
    context = {
        'user':user,
        'user':user
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
        print("Password:",password_in)

        department = Department.objects.get(id=department_id)
        user = User.objects.get(id=staff_id)
        user.email = email
        user.is_staff = True
        user.is_superuser = False
        
        staff = Staff.objects.get(id = staff_id)
        
        if password_in is None or password_in == '':
            password = name
            user.password = password
            user.save()
        else:
            user.password = password_in
            staff.access_to_web = True
            user.save()
              
        
        staff.name = name
        staff.gaurd_name = gaurd_name
        staff.address = address
        staff.gender = gender
        staff.phone = phone
        staff.department = department
        staff.user = user

        if profile_pic:
            staff.profile_pic = profile_pic
        staff.save()
        
        messages.success(request,"Record Are Successfully Updated !")
        return redirect('view_staff')
        
    return render(request,'admin/edit_staff.html')


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
        'user':user
    }
    return render(request,'admin/add_scheme.html',context=context)

@login_required
def delete_scheme(request,id):
    scheme = Scheme.objects.get(id = id)
    scheme.delete()
    messages.success(request,'Scheme Deleted !!')
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