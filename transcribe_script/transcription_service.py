from openai import OpenAI
import moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from datetime import datetime
import math


def extract_audio(video_path):
    # Check if it's already an audio file
    audio_extensions = ['.mp3', '.wav', '.m4a', '.webm', '.mpeg', '.mpga',]
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


def split_video_into_chunks(video_path, chunk_size_mb=90):
    """
    Split a video into smaller chunks based on file size.
    Returns list of chunk file paths.
    """
    chunk_paths = []
    
    try:
        video = VideoFileClip(video_path)
        total_duration = video.duration
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        # Calculate how many chunks we need
        num_chunks = math.ceil(file_size_mb / chunk_size_mb)
        
        if num_chunks == 1:
            # File is small enough, no splitting needed
            video.close()
            return [video_path]
        
        # Calculate duration per chunk
        chunk_duration = total_duration / num_chunks
        
        base_path = os.path.splitext(video_path)[0]
        
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, total_duration)
            
            chunk_path = f"{base_path}_chunk_{i+1}.mp4"
            
            # Extract chunk
            chunk = video.subclip(start_time, end_time)
            chunk.write_videofile(
                chunk_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            chunk.close()
            
            chunk_paths.append(chunk_path)
        
        video.close()
        return chunk_paths
        
    except Exception as e:
        raise Exception(f"Failed to split video: {str(e)}")


def process_transcription(transcription_obj):
    """Main function that processes a Transcription object"""
    try:
        # Update status
        transcription_obj.status = 'processing'
        transcription_obj.save()
        
        video_path = transcription_obj.video_file.path
        
        # Step 1: Split video into chunks if needed
        chunk_paths = split_video_into_chunks(video_path, chunk_size_mb=90)
        
        all_raw_transcripts = []
        
        # Step 2: Process each chunk
        for chunk_path in chunk_paths:
            # Extract audio from chunk
            audio_path = extract_audio(chunk_path)
            
            # Transcribe with Whisper
            raw_transcript = transcribe_with_whisper(
                audio_path, 
                transcription_obj.api_key
            )
            all_raw_transcripts.append(raw_transcript)
            
            # Clean up chunk files
            if audio_path != chunk_path:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            
            # Delete chunk if it's not the original file
            if chunk_path != video_path:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
        
        # Step 3: Combine all transcripts
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
        
        # Step 6: Delete the original uploaded file
        transcription_obj.video_file.delete(save=False)
        
        return True
        
    except Exception as e:
        # If anything goes wrong, save the error
        transcription_obj.status = 'failed'
        transcription_obj.error_message = str(e)
        transcription_obj.save()
        return False