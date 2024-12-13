# urls.py
from django.urls import path
from . import views

app_name = 'core'  # Ensure the app name is set correctly

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('sign_up/', views.sign_up, name='signup'),
    path('sign_in/', views.sign_in, name='signin'),
    
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('scientist_dashboard/', views.scientist_dashboard, name='scientist_dashboard'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/accept/<int:appointment_id>/', views.accept_appointment, name='accept_appointment'),
    path('add_issue/', views.add_issue, name='add_issue'),  # New URL for add_issue view
    path('add-research-post/', views.add_research_post, name='add_research_post'),\
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-doctor-profile/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('project_team/', views.project_team, name='project_team'),
    path('our_story/', views.our_story, name='our_story'),
    path('edit_researcher_profile/', views.edit_researcher_profile, name='edit_researcher_profile'),
    
]
