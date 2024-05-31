from django.urls import path
from userapp.views import *

urlpatterns = [
    path('',INDEX, name='home'),
    path('contact/',contact,name='contact'),
    path('about/',about,name='about'),
    path('course/',course,name='course'),
    path('certificate-issue/',certificate_issue, name='certificate_issue')
]