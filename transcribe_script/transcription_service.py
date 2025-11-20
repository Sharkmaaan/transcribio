from openai import OpenAI
import os
from datetime import datetime
from pydub import AudioSegment
    
def split_audio_into_chunks(audio_path, max_size_mb=20):
    """Split audio file into chunks if it exceeds max_size_mb"""
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

    # If file is small enough, return as-is
    if file_size_mb <= max_size_mb:
        return [audio_path]

    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Calculate chunk duration based on file size
    total_duration_ms = len(audio)
    num_chunks = int(file_size_mb / max_size_mb) + 1
    chunk_duration_ms = total_duration_ms // num_chunks

    chunks = []
    base_path = os.path.splitext(audio_path)[0]

    for i in range(num_chunks):
        start_ms = i * chunk_duration_ms
        end_ms = min((i + 1) * chunk_duration_ms, total_duration_ms)

        chunk = audio[start_ms:end_ms]
        chunk_path = f"{base_path}_chunk_{i}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)

    return chunks


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

        # Step 1: Get the file path
        file_path = transcription_obj.video_file.path

        # Step 2: Determine if it's audio or video and set appropriate chunk size
        audio_extensions = ['.mp3', '.wav', '.m4a', '.webm', '.mpeg', '.mpga']
        is_audio = any(file_path.lower().endswith(ext) for ext in audio_extensions)

        # MP3s: 20MB chunks, Videos: 100MB chunks
        max_chunk_size = 20 if is_audio else 100

        # Step 3: Split file into chunks if needed
        file_chunks = split_audio_into_chunks(file_path, max_size_mb=max_chunk_size)

        all_raw_transcripts = []

        # Step 4: Transcribe each chunk with Whisper
        for chunk_path in file_chunks:
            raw_transcript = transcribe_with_whisper(
                chunk_path,
                transcription_obj.api_key
            )
            all_raw_transcripts.append(raw_transcript)

            # Clean up chunk if it's not the original file
            if chunk_path != file_path:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)

        # Combine all transcripts
        combined_raw_transcript = "\n\n".join(all_raw_transcripts)
        transcription_obj.raw_transcript = combined_raw_transcript
        transcription_obj.save()

        # Step 5: Polish with ChatGPT
        polished_transcript = polish_with_chatgpt(
            combined_raw_transcript,
            transcription_obj.api_key
        )
        transcription_obj.polished_transcript = polished_transcript

        # Step 6: Mark as completed
        transcription_obj.status = 'completed'
        transcription_obj.completed_at = datetime.now()
        transcription_obj.api_key = ""  # Clear the API key for security
        transcription_obj.save()

        # Step 7: Clean up files to save storage
        # Delete the original uploaded file
        transcription_obj.video_file.delete(save=False)

        return True

    except Exception as e:
        # If anything goes wrong, save the error
        transcription_obj.status = 'failed'
        transcription_obj.error_message = str(e)
        transcription_obj.save()
        return False