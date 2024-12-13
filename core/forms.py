from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# Choices for the user roles
ROLE_CHOICES = [
    ('doctor', 'Doctor'),
    ('patient', 'Patient'),
    ('scientist', 'Scientist'),
]

class SignUpForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Role")
    
    # Doctor-specific fields
    license_number = forms.CharField(max_length=20, required=False, label="License Number")
    specialization = forms.CharField(max_length=100, required=False, label="Specialization")
    hospital = forms.CharField(max_length=100, required=False, label="Hospital")

    # Scientist-specific fields
    research_area = forms.CharField(max_length=100, required=False, label="Research Area")
    institution = forms.CharField(max_length=100, required=False, label="Institution")

    # Patient-specific fields
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=False)
    age = forms.IntegerField(required=False, label="Age")
    address = forms.CharField(widget=forms.Textarea, required=False, label="Address")
    medical_history = forms.CharField(widget=forms.Textarea, required=False, label="Medical History")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        # Custom validation for required fields based on role
        if role == 'doctor':
            if not cleaned_data.get("license_number") or not cleaned_data.get("specialization"):
                raise forms.ValidationError("Doctor's license number and specialization are required.")
        elif role == 'scientist':
            if not cleaned_data.get("research_area") or not cleaned_data.get("institution"):
                raise forms.ValidationError("Scientist's research area and institution are required.")
        elif role == 'patient':
            if not cleaned_data.get("gender") or not cleaned_data.get("age"):
                raise forms.ValidationError("Patient's gender and age are required.")

        return cleaned_data

from django import forms
from .models import Issue

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['description', 'report']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
from django import forms
from .models import Medication, UserProfile

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['patient', 'name', 'dosage', 'frequency', 'instructions']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control custom-select'}),  # Add Bootstrap class
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter medication name'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter dosage amount'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter frequency (e.g., daily)'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter medication instructions', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(MedicationForm, self).__init__(*args, **kwargs)
        
        # Restrict patient options to only those with role 'patient'
        self.fields['patient'].queryset = UserProfile.objects.filter(role='patient')

        # Remove labels from form fields
        for field in self.fields.values():
            field.label = False


from django import forms
from .models import ResearchPost

class ResearchPostForm(forms.ModelForm):
    class Meta:
        model = ResearchPost
        fields = ['title', 'content']  # Including fields for title and content
    
    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        if user_profile:
            self.instance.scientist = user_profile  # Automatically set the scientist field


from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'gender', 'age', 'address']
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your full name',
                }
            ),
            'gender': forms.Select(
                choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                attrs={'class': 'form-select'}
            ),
            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your age',
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter your address',
                }
            ),
        }

from django import forms
from .models import UserProfile

# forms.py
class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'license_number', 'specialization', 'hospital']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Enter your full name',
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Enter your license number',
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Enter your specialization',
            }),
            'hospital': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Enter your hospital name',
            }),
        }

from django import forms
from .models import UserProfile




class ResearcherProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'research_area', 'institution']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
            }),
            'research_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your research area',
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your institution',
            }),
        }

from django import forms
from .models import Appointment
from datetime import datetime

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'status']  # Exclude 'doctor' field from form
    
    appointment_date = forms.DateTimeField(
        initial=datetime.now,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',  # Add Bootstrap class directly here
        })
    )

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Apply Bootstrap styling

