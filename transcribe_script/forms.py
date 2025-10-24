from django import forms
from .models import Transcription


class TranscriptionForm(forms.ModelForm):
    class Meta:
        model = Transcription
        fields = ['video_file', 'api_key']
        widgets = {
            'api_key': forms.PasswordInput(attrs={
                'placeholder': 'sk-...',
                'class': 'form-control'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.mp4'
            })
        }
        labels = {
            'video_file': 'Upload your MP4 video',
            'api_key': 'Your OpenAI API Key'
        }
        help_texts = {
            'api_key': 'Get your API key from platform.openai.com',
            'video_file': 'Maximum file size: 100MB'
        }