from django.urls import path
from .views import *
from userapp.views import *

urlpatterns = [
    
    
    # login
    
    path('',custom_login, name='login'),
    path('',logout, name='logout'),
    
    path('admin/home',home,name='admin_home'),
    path('student-admission/',student_admission,name='student_admission'),
    path('view-students/',view_student,name='view_student'),
    path('edit-student/<int:id>',edit_student,name='edit_student'),
    path('update-student/',update_student,name='update_student'),
    path('delete-student/<int:admin>',delete_student,name='delete_student'),
    
    # course
    path('add-course/',add_course,name='add_course'),
    path('view-course/',view_course,name='view_course'),
    path('Course/Edit/<str:id>',edit_course,name='edit_course'),
    path('Course/Update',update_course,name='update_course'),
    path('Course/Delete/<str:id>',delete_course,name='delete_course'),
    
    # payment
    path('payment/<str:id>',fee_payment,name='fee_payment'),
    path('view-reciept/<int:id>',view_reciept,name="view_receipt"),
    # path('pdf/<int:id>', generate_pdf, name='download_pdf'),
    path('payed-list/',payed_list,name='payed_list'),
    # path('download_receipt/<int:payment_id>/', download_receipt, name='download_receipt'),
    
    # branch
    path('add-branch/',add_branch,name='add_branch'),
    path('update-branch/<int:id>',update_branch,name='update_branch'),
    path('branch/delete/<str:id>',delete_branch,name='delete_branch'),
    
    # view_contacs
    path('view-contacts/',view_contacts,name='view_contacts'),
    path('contact-followup/<int:id>',contact_followup,name='followup'),
    path('delete-contact/<int:id>',delete_contact,name="delete_contact"),
    
    # staff
    path('add-staff/',add_staff,name='add_staff'),
    path('view-staff/',view_staff,name='view_staff'),
    path('edit-staff/<int:id>',edit_staff,name='edit_staff'),
    path('update-staff/',update_staff,name='update_staff'),
    path('delete-staff/<int:admin>',delete_staff,name='delete_staff'),
    
    # department
    path('add-department/',add_department,name='add_department'),
    path('view-department/',view_department,name='view_department'),
    path('department/edit/<str:id>',edit_department,name='edit_department'),
    path('department/update',update_department,name='update_department'),
    path('department/delete/<str:id>',delete_department,name='delete_department'),
    
    # scheme
    path('scheme/',scheme,name='scheme'),
    path('delete-scheme/<int:id>',delete_scheme,name='delete_scheme'),
    
    # testimonals
    path('testimonals/',testimonals,name='test'),
    path('delete-testimonal/<int:id>',delete_testimonal,name='delete_testimonial'),
    
    path('add-bgimage/',add_bg_image,name='add_bg_image'),
    path('title-change/',home_titles,name='home_titles'),
    path('delete-home-qoute/<int:id>',delete_home_qoute,name='delete_home_qoute'),
    path('delete-bgimage/<int:id>',delete_bg_image,name='delete_bg_image'),
    
    # enquiry
    path('add-enquiry/',add_enquiry,name='enquiry'),
    path('edit-enquiry/<int:id>',edit_enquiry,name='edit-enquiry'),
    path('delete-enquiry/<int:id>',delete_enquiry,name='delete-enquiry'),
    path('enquiry-admission/<int:id>',enq_to_admission,name='enq_to_admission')
] 