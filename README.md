# Transcribio

A Django web application that transcribes MP4 videos using OpenAI's Whisper API and polishes transcripts with ChatGPT.

## Features

- Upload MP4 videos
- Automatic transcription using Whisper AI
- AI-polished transcripts using ChatGPT
- Download both raw and polished versions
- User provides their own OpenAI API key

## Tech Stack

- Django 5.2.7
- OpenAI API (Whisper + GPT-4)
- MoviePy for audio extraction
- SQLite database

## Setup

1. Clone the repository
2. Install dependencies: `pip install django openai moviepy`
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`
5. Visit http://127.0.0.1:8000/

## Usage

1. Get an OpenAI API key from platform.openai.com
2. Upload your MP4 video
3. Enter your API key
4. Wait for processing (1-2 minutes)
5. Download your transcripts!

## Note

This is a learning project. Users must provide their own OpenAI API key.