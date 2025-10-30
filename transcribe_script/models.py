from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField


def validate_video_file(file):
    """Check if the uploaded file is a supported format"""
    allowed_extensions = ['.mp4', '.mp3', '.wav', '.m4a', '.webm', '.mpeg', '.mpga']
    
    file_extension = file.name.lower()
    if not any(file_extension.endswith(ext) for ext in allowed_extensions):
        raise ValidationError(
            f'Unsupported file format. Allowed formats: MP4, MP3, WAV, M4A, WebM, MPEG, MPGA'
        )


class Transcription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    video_file = models.FileField(
        upload_to='videos/',
        validators=[validate_video_file]
    )
    api_key = EncryptedCharField(max_length=200, help_text="Your OpenAI API key") 
    
    # Two versions of the transcript
    raw_transcript = models.TextField(blank=True, help_text="Direct output from Whisper")
    polished_transcript = models.TextField(blank=True, help_text="Cleaned up by ChatGPT")
    
    # Status tracking
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Transcription {self.id} - {self.status}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = EncryptedCharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"