from django.db import models
from adminapp.models import Course

# Create your models here.


class contacted_user(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=50)
    course = models.ForeignKey(Course,on_delete=models.DO_NOTHING)
    message = models.CharField(max_length=50)
    remarks = models.CharField(max_length=50, null=True)
    is_follow = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Home(models.Model):
    qoute1 = models.CharField(max_length=80,default="Learning Today, Leading Tomorrow")
    qoute2 = models.CharField(default="Skill Board Education",max_length=80)
    by = models.CharField(max_length=50)
    
    def __str__(self):
        return self.qoute1
    
class About(models.Model):
    about = models.TextField(default="skillboard education pandikkad",null=True)
    mission = models.TextField(default="skillboard education pandikkad",null=True)
    vision = models.TextField(default="skillboard education pandikkad",null=True)
    
    def __str__(self):
        return self.about
    
class Bgimages(models.Model):
    bgimage = models.ImageField(upload_to='Background')
    

class Testimonal(models.Model):
    photo = models.ImageField(upload_to='testimonals')
    name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    message = models.TextField()
    
    def __str__(self):
        return self.name