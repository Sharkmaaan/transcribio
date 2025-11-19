from django import forms
from .models import Transcription
from .models import UserProfile


class TranscriptionForm(forms.ModelForm):
    class Meta:
        model = Transcription
        fields = ['video_file']
        widgets = {
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*,audio/*,.mp4,.mp3,.wav,.m4a,.webm,.mkv'  
            })
        }
        labels = {
            'video_file': 'Upload your media file'  
        }
        help_texts = {
            'video_file': 'Supports: MP4, MP3, WAV, M4A, WebM, MPEG, MKV (max 100MB)'  
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['api_key']
        widgets = {
            'api_key': forms.PasswordInput(attrs={
                'placeholder': 'sk-...',
            })
        }
        labels = {
            'api_key': 'Your OpenAI API Key'
        }
        help_texts = {
            'api_key': 'Get your key from platform.openai.com/api-keys'
        }