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
    title = models.CharField(max_length=50,default="Learning Today, Leading Tomorrow")
    subtitle = models.CharField(default="Skill Board Education",max_length=50)
    about = models.TextField(default = "We are making skilled students for future")
    
    def __str__(self):
        return self.title
    
class Bgimages(models.Model):
    bgimage = models.ImageField(upload_to='Background')
    

class Testimonal(models.Model):
    photo = models.ImageField(upload_to='testimonals')
    name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    message = models.TextField()
    
    def __str__(self):
        return self.name