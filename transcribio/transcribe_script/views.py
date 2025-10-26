from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Transcription
from .forms import TranscriptionForm
from .transcription_service import process_transcription
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib import messages
from openai import OpenAI
import threading

def signup(request):
    """User registration page"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for the new user
            UserProfile.objects.create(user=user)
            # Log them in automatically
            login(request, user)
            # Redirect to profile to add API key
            return redirect('profile_settings')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def upload_video(request):
    """Page where users upload their video"""
    # Check if user has API key saved
    try:
        profile = request.user.userprofile
        if not profile.api_key:
            # Redirect to settings if no API key
            return redirect('profile_settings')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user)
        return redirect('profile_settings')
    
    if request.method == 'POST':
        form = TranscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            transcription = form.save(commit=False)
            transcription.api_key = profile.api_key  # Use saved API key
            transcription.user = request.user  # Link to user
            transcription.save()
            
            # Start transcription in background
            thread = threading.Thread(
                target=process_transcription,
                args=(transcription,)
            )
            thread.start()
            
            return redirect('transcription_status', pk=transcription.id)
    else:
        form = TranscriptionForm()
    
    return render(request, 'transcribe_script/upload.html', {'form': form})

def validate_openai_key(api_key):
    """Test if an OpenAI API key is valid"""
    try:
        client = OpenAI(api_key=api_key)
        # Make a minimal API call to test the key
        client.models.list()  # Lists models as cheap test
        return True, None  # Valid key
    except Exception as e:
        error_message = str(e)
        if "incorrect_api_key" in error_message or "invalid_api_key" in error_message:
            return False, "API key not valid. Please check your key and try again."
        elif "insufficient_quota" in error_message:
            return False, "API key is valid but has no credits. Please add credits to your OpenAI account."
        else:
            return False, f"Error validating API key: {error_message}"

@login_required
def profile_settings(request):
    """User profile settings - save API key"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Get the API key before saving
            api_key = form.cleaned_data['api_key']
            
            # Validate the API key
            is_valid, error_message = validate_openai_key(api_key)
            
            if is_valid:
                form.save()
                messages.success(request, '✅ API key saved!')
                return redirect('upload_video')
            else:
                # Show error message
                messages.error(request, error_message)
                # Don't save, show form again with error
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'transcribe_script/profile.html', {'form': form})

def transcription_status(request, pk):
    """Page showing transcription progress"""
    transcription = get_object_or_404(Transcription, pk=pk)
    return render(request, 'transcribe_script/status.html', {
        'transcription': transcription
    })

def logout_view(request):
    """Log out the user"""
    logout(request)
    return redirect('login')

def download_transcript(request, pk, transcript_type):
    """Download a transcript as a text file"""
    transcription = get_object_or_404(Transcription, pk=pk)
    
    if transcript_type == 'raw':
        content = transcription.raw_transcript
        filename = f"transcript_raw_{pk}.txt"
    else:
        content = transcription.polished_transcript
        filename = f"transcript_polished_{pk}.txt"
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response