from openai import OpenAI
import moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from datetime import datetime
from pydub import AudioSegment

def split_audio_into_chunks(audio_path, max_size_mb=20):
    """
    Split audio file into chunks under OpenAI's 25MB limit.
    Returns list of chunk file paths.
    """
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    
    # If file is small enough, no splitting needed
    if file_size_mb <= max_size_mb:
        return [audio_path]
    
    chunk_paths = []
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        total_duration_ms = len(audio)
        
        # Calculate how many chunks we need (20MB chunks for safety margin)
        import math
        num_chunks = math.ceil(file_size_mb / max_size_mb)
        chunk_duration_ms = total_duration_ms / num_chunks
        
        base_path = os.path.splitext(audio_path)[0]
        file_ext = os.path.splitext(audio_path)[1]
        
        for i in range(num_chunks):
            start_ms = int(i * chunk_duration_ms)
            end_ms = int(min((i + 1) * chunk_duration_ms, total_duration_ms))
            
            chunk_path = f"{base_path}_chunk_{i+1}{file_ext}"
            
            # Extract and export chunk
            chunk = audio[start_ms:end_ms]
            chunk.export(chunk_path, format=file_ext.replace('.', ''))
            
            chunk_paths.append(chunk_path)
        
        return chunk_paths
        
    except Exception as e:
        raise Exception(f"Failed to split audio: {str(e)}")
    
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
        
        # Step 1: Extract audio from video (or use audio directly if already audio)
        video_path = transcription_obj.video_file.path
        audio_path = extract_audio(video_path)
        
        # Step 2: Split audio into chunks if needed
        audio_chunks = split_audio_into_chunks(audio_path, max_size_mb=20)
        
        all_raw_transcripts = []
        
        # Step 3: Transcribe each chunk with Whisper
        for chunk_path in audio_chunks:
            raw_transcript = transcribe_with_whisper(
                chunk_path, 
                transcription_obj.api_key
            )
            all_raw_transcripts.append(raw_transcript)
            
            # Clean up chunk if it's not the original audio
            if chunk_path != audio_path:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
        
        # Combine all transcripts
        combined_raw_transcript = "\n\n".join(all_raw_transcripts)
        transcription_obj.raw_transcript = combined_raw_transcript
        transcription_obj.save()
        
        # Step 4: Polish with ChatGPT
        polished_transcript = polish_with_chatgpt(
            combined_raw_transcript,
            transcription_obj.api_key
        )
        transcription_obj.polished_transcript = polished_transcript
        
        # Step 5: Mark as completed
        transcription_obj.status = 'completed'
        transcription_obj.completed_at = datetime.now()
        transcription_obj.api_key = ""  # Clear the API key for security
        transcription_obj.save()
        
        # Step 6: Clean up files to save storage
        # Delete extracted audio file if it's different from original
        if audio_path != video_path:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        
        # Delete the original uploaded file
        transcription_obj.video_file.delete(save=False)
        
        return True
        
    except Exception as e:
        # If anything goes wrong, save the error
        transcription_obj.status = 'failed'
        transcription_obj.error_message = str(e)
        transcription_obj.save()
        return False