from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from .models import UserProfile, Appointment, Issue
from .forms import SignUpForm, IssueForm

# Base Views
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Authentication Views
def sign_up(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        # Create user and profile
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()
        
        user_profile = UserProfile.objects.create(user=user, role=role, full_name=name)

        # Role-specific information
        if role == 'doctor':
            user_profile.license_number = request.POST.get('license_number', '')
            user_profile.specialization = request.POST.get('specialization', '')
            user_profile.hospital = request.POST.get('hospital', '')
        elif role == 'scientist':
            user_profile.research_area = request.POST.get('research_area', '')
            user_profile.institution = request.POST.get('institution', '')
        elif role == 'patient':
            user_profile.gender = request.POST.get('gender', '')
            user_profile.age = request.POST.get('age', None)
            user_profile.address = request.POST.get('address', '')
            user_profile.medical_history = request.POST.get('medical_history', '')

        user_profile.save()

        # Authentication and redirect
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse(f'core:{role}_dashboard'))
        return render(request, 'signup.html', {'error': 'Authentication failed'})

    return render(request, 'signup.html')

def sign_in(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('core:login')

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            
            try:
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.role in ['doctor', 'patient', 'scientist']:
                    return redirect(f'core:{user_profile.role}_dashboard')
                messages.error(request, "Role not assigned correctly.")
                return redirect('core:login')
            except UserProfile.DoesNotExist:
                messages.error(request, "User profile does not exist.")
                return redirect('core:signin')

        messages.error(request, "Invalid email or password.")
        return redirect('core:signin')

    return render(request, 'signin.html')

# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Appointment, Issue, Medication, ResearchPost, Notification  # Import Medication
from .forms import MedicationForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Appointment, Issue, Medication, ResearchPost, Notification
from .forms import MedicationForm

@login_required
def doctor_dashboard(request):
    # Get the logged-in user's profile and ensure they are a doctor
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='doctor')
    except UserProfile.DoesNotExist:
        return render(request, 'unauthorized.html')

    # Fetch all appointments related to the logged-in doctor
    appointments = Appointment.objects.filter(doctor=user_profile)
    appointment_details = []

    # Gather detailed information for each appointment
    for appointment in appointments:
        patient_profile = appointment.patient
        issues = Issue.objects.filter(patient=patient_profile)
        medications = Medication.objects.filter(patient=patient_profile)

        appointment_details.append({
            'appointment': appointment,
            'patient_profile': patient_profile,
            'issues': issues,
            'medications': medications,
        })

    # Handle Medication Form submission
    if request.method == 'POST':
        medication_form = MedicationForm(request.POST)
        if medication_form.is_valid():
            medication_form.save()
            return redirect('core:doctor_dashboard')
    else:
        medication_form = MedicationForm()

    # Fetch research posts and notifications
    research_posts = ResearchPost.objects.all().order_by('-created_at')[:5]
    notifications = Notification.objects.filter(user_profile=user_profile).order_by('-created_at')[:5]
    unread_notifications_count = Notification.objects.filter(user_profile=user_profile, is_read=False).count()

    # Pass data to the template
    context = {
        'profile': user_profile,
        'appointment_details': appointment_details,
        'medication_form': medication_form,
        'research_posts': research_posts,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'doctor_dashboard.html', context)




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Medication, Appointment, Issue

from django.shortcuts import render, redirect
from core.models import UserProfile, Issue, Medication, Appointment

@login_required
def patient_dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='patient')
    except UserProfile.DoesNotExist:
        return redirect('core:signin')

    # Fetch issues related to the patient
    patient_issues = Issue.objects.filter(patient=user_profile)

    # Fetch doctors based on specialization matching patient issues
    issue_descriptions = patient_issues.values_list('description', flat=True)
    doctors = UserProfile.objects.filter(
        role='doctor',
        specialization__in=issue_descriptions  # Match doctor's specialization with issue descriptions
    )

    context = {
        'profile': user_profile,
        'medical_history': user_profile.medical_history,
        'appointments': Appointment.objects.filter(patient=user_profile),
        'issues': patient_issues,
        'medications': Medication.objects.filter(patient=user_profile),
        'doctors': doctors,
    }

    return render(request, 'patient_dashboard.html', context)




from django.shortcuts import render, redirect
from .models import UserProfile, Notification, ResearchPost

@login_required
def scientist_dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='scientist')
    except UserProfile.DoesNotExist:
        return redirect('core:signin')

    # Get unread notifications for the logged-in scientist
    unread_notifications_count = Notification.objects.filter(user_profile=user_profile, is_read=False).count()

    # Fetch all research posts (removing the scientist filter)
    research_posts = ResearchPost.objects.all()

    # Pass context
    context = {
        'profile': user_profile,
        'research_area': user_profile.research_area,
        'institution': user_profile.institution,
        'research_posts': research_posts,  # Fetching all research posts
        'unread_notifications_count': unread_notifications_count,  # Unread notifications count
    }

    return render(request, 'scientist_dashboard.html', context)


@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user_profile__user=request.user)
        notification.is_read = True
        notification.save()
    except Notification.DoesNotExist:
        pass
    
    return redirect('core:scientist_dashboard')


# views.py
from django.shortcuts import render
from .models import Appointment
from .forms import AppointmentForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from .models import UserProfile, Appointment
from .forms import AppointmentForm
from django.contrib.auth.decorators import login_required

@login_required
def book_appointment(request, doctor_id):
    # Get the doctor object based on the ID
    doctor = get_object_or_404(UserProfile, id=doctor_id, role='doctor')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Save the form but don't commit yet
            appointment = form.save(commit=False)
            # Assign the doctor and the patient (current user)
            appointment.doctor = doctor
            appointment.patient = UserProfile.objects.get(user=request.user, role='patient')
            appointment.save()
            return redirect('core:patient_dashboard')
    else:
        # Prefill the doctor field
        form = AppointmentForm(initial={'doctor': doctor})

    return render(request, 'book_appointment.html', {'form': form, 'doctor': doctor})



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required



@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the user's profile matches the appointment's patient
    user_profile = request.user.userprofile
    if user_profile != appointment.patient:
        messages.error(request, "You don't have permission to cancel this appointment.")
        return redirect('core:patient_dashboard')
    
    if appointment.status == "Scheduled":
        appointment.status = "Cancelled"
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "You cannot cancel this appointment.")
    
    return redirect('core:patient_dashboard')

@login_required
def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the user's profile matches the appointment's doctor
    user_profile = request.user.userprofile
    if user_profile != appointment.doctor:
        messages.error(request, "You don't have permission to accept this appointment.")
        return redirect('core:doctor_dashboard')
    
    if appointment.status == "Scheduled":
        appointment.status = "Accepted"
        appointment.save()
        messages.success(request, "Appointment accepted successfully.")
    else:
        messages.error(request, "This appointment cannot be accepted.")
    
    return redirect('core:doctor_dashboard')

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def add_issue(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        report = request.FILES.get('report', None)

        user_profile = UserProfile.objects.get(user=request.user, role='patient')

        # Create and save the issue
        new_issue = Issue.objects.create(
            patient=user_profile,
            description=description,
            report=report
        )
        new_issue.save()

        return redirect('core:patient_dashboard')
    return redirect('core:patient_dashboard')




from django.shortcuts import render, redirect
from .models import ResearchPost, UserProfile, Notification
from django.contrib.auth.decorators import login_required

@login_required
def add_research_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        # Assuming a logged-in scientist is posting
        user_profile = UserProfile.objects.get(user=request.user, role='scientist')

        # Create the research post
        post = ResearchPost.objects.create(scientist=user_profile, title=title, content=content)
        
        # Create notification for all scientists
        Notification.objects.create(
            user_profile=user_profile,
            message=f"New Medicine Discovery: {post.title} posted by {user_profile.full_name}"
        )

        return redirect('core:scientist_dashboard')

    return render(request, 'add_research_post.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm,DoctorProfileForm

@login_required
def edit_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('core:signin')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('core:patient_dashboard')  # Redirect to the dashboard after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('core:signin')  # Replace with the name of your login/signin URL

@login_required
def edit_doctor_profile(request):
    try:
        # Fetch the doctor's profile based on the logged-in user
        user_profile = UserProfile.objects.get(user=request.user, role='doctor')
    except UserProfile.DoesNotExist:
        # If the doctor profile does not exist, redirect to sign in
        return redirect('core:signin')

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()  # Save the form and update the doctor's profile
            return redirect('core:doctor_dashboard')  # Redirect to doctor's dashboard after saving
    else:
        form = DoctorProfileForm(instance=user_profile)

    return render(request, 'edit_doctor_profile.html', {'form': form})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import ResearcherProfileForm

@login_required
def edit_researcher_profile(request):
    try:
        # Ensure the user is a researcher by checking the role
        user_profile = UserProfile.objects.get(user=request.user, role='researcher')
    except UserProfile.DoesNotExist:
        # If the user profile is not found, redirect to the sign-in page
        return redirect('core:signin')  # You can modify this if you want to show an error message instead

    if request.method == 'POST':
        form = ResearcherProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('researcher_dashboard')  # Redirect to the researcher dashboard after saving
    else:
        form = ResearcherProfileForm(instance=user_profile)

    return render(request, 'researcher_profile.html', {'form': form})

def project_team(request):
    return render(request, 'Project_team.html')

def our_story(request):
    return render(request, 'our_story.html')