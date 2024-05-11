from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=150)
    duration = models.CharField(max_length=50)
    fee = models.IntegerField()
    photo = models.ImageField(upload_to='courses',null=True)
    description = models.TextField(null=True)
    
    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

class Branch(models.Model):
    branch_name = models.CharField(max_length=50)
    branch_code = models.CharField(max_length=10)
    photo = models.ImageField(upload_to='branches', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.branch_name
    
class Department(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Scheme(models.Model):
    name = models.CharField(max_length=50)
    scheme = models.FloatField()
    photo = models.ImageField(upload_to='Scheme')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 
    
class Student(models.Model):
    profile_pic = models.ImageField(upload_to='profile_pic')
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254,null=True)
    gaurd_name = models.CharField(max_length=50,null=True)
    address = models.TextField(null=True)
    gender = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    dob = models.DateField(null=True)
    age = models.TextField(max_length=20,null=True)
    other_fee = models.IntegerField(null=True)
    course_id = models.ForeignKey(Course,on_delete=models.DO_NOTHING)
    branch_id = models.ForeignKey(Branch,on_delete=models.DO_NOTHING)
    scheme_id = models.ForeignKey(Scheme,on_delete=models.DO_NOTHING)
    final_fee = models.IntegerField()
    certificate_issued = models.BooleanField(default=False)
    course_completed = models.BooleanField(default=False)
    examination_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Payment(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    amount = models.IntegerField()
    pay_option = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.student.name

class Staff(models.Model):
    profile_pic = models.ImageField(upload_to='profile_pic')
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gaurd_name = models.CharField(max_length=50)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    dob = models.DateField()
    age = models.TextField(max_length=20)
    access_to_web = models.BooleanField(default=False)
    department = models.ForeignKey(Department,on_delete=models.DO_NOTHING)
    branch_id = models.ForeignKey(Branch,on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 
    

class Enquiry(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    remarks = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 
    
    