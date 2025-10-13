from django.db import models
from django.core.exceptions import ValidationError


def validate_video_file(file):
    """Check if the uploaded file is an MP4"""
    if not file.name.endswith('.mp4'):
        raise ValidationError('Only MP4 files are allowed.')


class Transcription(models.Model):
    # File and API key
    video_file = models.FileField(
        upload_to='videos/',
        validators=[validate_video_file]
    )
    api_key = models.CharField(max_length=200, help_text="Your OpenAI API key")
    
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