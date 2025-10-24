from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Transcription
from .forms import TranscriptionForm
from .transcription_service import process_transcription
import threading


def upload_video(request):
    """Page where users upload their video"""
    if request.method == 'POST':
        form = TranscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the transcription
            transcription = form.save()
            
            # Start transcription in background thread
            thread = threading.Thread(
                target=process_transcription,
                args=(transcription,)
            )
            thread.start()
            
            # Redirect to status page
            return redirect('transcription_status', pk=transcription.id)
    else:
        form = TranscriptionForm()
    
    return render(request, 'transcribe_script/upload.html', {'form': form})


def transcription_status(request, pk):
    """Page showing transcription progress"""
    transcription = get_object_or_404(Transcription, pk=pk)
    return render(request, 'transcribe_script/status.html', {
        'transcription': transcription
    })


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