Transcripio
Live Demo: www.transcripio.com
A Django-based web application that automatically transcribes video and audio files using OpenAI's Whisper API, with optional AI-powered transcript polishing via ChatGPT.

🎯 Project Overview
Transcriptio was built to solve a real-world problem: efficiently transcribing interview recordings for content creation projects. As a professional copywriter transitioning into web development, I needed a tool that could handle both raw transcription and produce polished, readable text.

Key Features

Video & Audio Upload: Supports multiple file formats (MP4, MP3, WAV, etc.)
Dual Transcription Output:

Raw transcription via Whisper API
AI-polished version via ChatGPT (optional)


API Key Management: Users provide their own OpenAI API keys (encrypted at rest)
Secure File Handling: Automatic cleanup and encrypted storage
Responsive Design: Works seamlessly on desktop and mobile devices

🛠️ Tech Stack
Backend

Django 5.x - Web framework
Python 3.11+ - Core language
PostgreSQL - Production database
Cryptography - Field-level encryption for sensitive data

Frontend

HTML5/CSS3 - Structure and styling
JavaScript - Interactive UI elements
Bootstrap - Responsive design

APIs & Services

OpenAI Whisper API - Audio transcription
OpenAI GPT-4 - Transcript polishing
MoviePy - Video/audio processing

Deployment

Digital Ocean - Hosting infrastructure
Appliku - Deployment automation
Cloudflare - DNS and CDN
WhiteNoise - Static file serving

🚀 Getting Started
Prerequisites
bashPython 3.11+
PostgreSQL (for production) or SQLite (for development)
OpenAI API account
Installation

Clone the repository

bashgit clone https://github.com/Sharkmaaan/transcripio.git
cd transcripio

Create a virtual environment

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies

bashpip install -r requirements.txt

Set up environment variables

Create a .env file in the project root:
envSECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FIELD_ENCRYPTION_KEY=your-encryption-key-here
DATABASE_URL=sqlite:///db.sqlite3  # or your PostgreSQL URL

Run migrations

bashpython manage.py migrate

Create a superuser

bashpython manage.py createsuperuser

Run the development server

bashpython manage.py runserver
Visit http://127.0.0.1:8000 to see the application.
📖 Usage

Create an account - Sign up and verify your email address
Add your API key - Securely store your OpenAI API key in your profile
Upload a file - Choose a video or audio file to transcribe
Select options - Choose whether you want a polished transcript
Download results - Get both raw and polished transcripts

🔐 Security Features

Encrypted API Keys: User API keys are encrypted using Fernet symmetric encryption
Email Verification: Prevents spam accounts and confirms user identity
CSRF Protection: Django's built-in CSRF protection for all forms
Environment Variables: Sensitive credentials stored outside version control
Secure File Handling: Uploaded files are processed and deleted securely

🎓 Learning Journey
Key challenges I solved:

User Authentication: Implemented Django's auth system with custom email verification
API Integration: Connected to OpenAI's APIs with proper error handling
File Processing: Handled large video files with MoviePy and FFmpeg
Encryption: Implemented field-level encryption for sensitive data
Deployment: Successfully deployed to production using Docker and cloud infrastructure
Git Workflow: Practiced proper version control and open source contribution practices

🤝 Contributing
This is a portfolio project, but feedback and suggestions are welcome! Feel free to:

Open an issue to report bugs
Suggest new features
Submit pull requests for improvements

📝 License
This project is open source and available under the MIT License.
👤 Author
Sanjay Ghosh

GitHub: @Sharkmaaan
Email: contact@sanjayghosh.com
Website: www.transcripio.com
