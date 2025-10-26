from openai import OpenAI
from moviepy.editor import VideoFileClip
import os
from datetime import datetime


def extract_audio(video_path):
    # Check if it's already an audio file
    audio_extensions = ['.mp3', '.wav', '.m4a', '.webm', '.mpeg', '.mpga']
    if any(video_path.lower().endswith(ext) for ext in audio_extensions):
        # It's already audio, just return the path
        return video_path
    
    
    # It's a video file, extract audio
    audio_path = os.path.splitext(video_path)[0] + '.mp3'
    
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()
    except Exception as e:
        raise Exception(f"Failed to extract audio: {str(e)}")
    
    return audio_path



def transcribe_with_whisper(audio_path, api_key):
    """Send audio to Whisper API and get raw transcript"""
    client = OpenAI(api_key=api_key)
    
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    return transcript.text


def polish_with_chatgpt(raw_transcript, api_key):
    """Send raw transcript to ChatGPT for cleanup"""
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a professional transcript editor. Clean up the following transcript by fixing grammar, adding proper punctuation, and formatting it nicely. Maintain all the original content and meaning and keep the language the same as the source."
            },
            {
                "role": "user",
                "content": raw_transcript
            }
        ]
    )
    
    return response.choices[0].message.content


def process_transcription(transcription_obj):
    """Main function that processes a Transcription object"""
    try:
        # Update status
        transcription_obj.status = 'processing'
        transcription_obj.save()
        
        # Step 1: Extract audio from video
        video_path = transcription_obj.video_file.path
        audio_path = extract_audio(video_path)
        
        # Step 2: Transcribe with Whisper
        raw_transcript = transcribe_with_whisper(
            audio_path, 
            transcription_obj.api_key
        )
        transcription_obj.raw_transcript = raw_transcript
        transcription_obj.save()
        
        # Step 3: Polish with ChatGPT
        polished_transcript = polish_with_chatgpt(
            raw_transcript,
            transcription_obj.api_key
        )
        transcription_obj.polished_transcript = polished_transcript
        
        # Step 4: Mark as completed
        transcription_obj.status = 'completed'
        transcription_obj.completed_at = datetime.now()
        transcription_obj.api_key = ""  # Clear the API key for security
        transcription_obj.save()
        
        # Clean up audio file
        if audio_path != video_path:
            os.remove(audio_path)
        
        return True
        
    except Exception as e:
        # If anything goes wrong, save the error
        transcription_obj.status = 'failed'
        transcription_obj.error_message = str(e)
        transcription_obj.save()
        return False