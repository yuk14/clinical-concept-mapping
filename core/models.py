from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    
    # Doctor-specific fields
    license_number = models.CharField(max_length=50, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    hospital = models.CharField(max_length=100, blank=True, null=True)
    
    # Scientist-specific fields
    research_area = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=100, blank=True, null=True)
    
    # Patient-specific fields
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Appointment Model - Now using UserProfile for both doctor and patient
class Appointment(models.Model):
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="appointments_as_patient")
    doctor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="appointments_as_doctor")
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, default="Scheduled")

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.first_name} {self.doctor.user.last_name} on {self.appointment_date}"

# Define the Issue model
class Issue(models.Model):
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'}, related_name='issues')
    description = models.TextField()
    report = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username}'s Issue"
    


# Medication Model
class Medication(models.Model):
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='medications')  # Relating Medication to Patient
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    instructions = models.TextField()

    def __str__(self):
        return f"Medication for {self.patient.user.username}: {self.name}"
    

from django.db import models
from django.contrib.auth.models import User
from .models import UserProfile  # Importing UserProfile model

class ResearchPost(models.Model):
    # Relating to the UserProfile model for scientists
    scientist = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'Scientist'})
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user_profile.user.username}: {self.message}"
