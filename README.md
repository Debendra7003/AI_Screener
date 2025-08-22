# AI Interview Screener - Backend API

A Django REST Framework-based backend system for conducting AI-powered voice interviews with real-time transcription, scoring, and recommendations.

## Features

- **Job Description Processing**: Upload JD and generate relevant interview questions using AI
- **Resume Parsing**: Upload PDF/DOCX resumes with automatic data extraction
- **Candidate Management**: Create and manage candidate profiles with E.164 phone validation
- **Voice Interviews**: Real outbound calls using Twilio with TTS questions and STT answers
- **AI Scoring**: Automatic answer evaluation and final hiring recommendations
- **Security**: API key authentication and phone number whitelisting
- **Webhooks**: Complete Twilio integration for call events and recordings

## Quick Start

### Prerequisites

- Python 3.8+
- Redis (for Celery)
- Twilio Account
- OpenAI API Key

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd AI-Interview-Screener
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. **Run Server**
```bash
python manage.py runserver
```

## Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# API Security
API_KEY=your-api-key

# Twilio (Required)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# OpenAI (Required)
OPENAI_API_KEY=your-openai-key

# Phone Whitelist (E.164 format)
WHITELISTED_PHONE_NUMBERS=+1234567890,+1987654321

# Redis
REDIS_URL=redis://localhost:6379/0
```

## API Endpoints

### Core Workflow

1. **Generate Questions**: `POST /api/generate-questions/`
2. **Create Candidate**: `POST /api/candidates/`
3. **Upload Resume**: `POST /api/candidates/{id}/upload-resume/`
4. **Create Interview**: `POST /api/interviews/create/`
5. **Trigger Call**: `POST /api/interviews/{id}/trigger/`
6. **Get Results**: `GET /api/interviews/{id}/results/`

### Authentication

All API endpoints require the `X-API-Key` header:
```
X-API-Key: your-api-key
```

## Deployment

### Using Heroku

1. **Install Heroku CLI and login**
```bash
heroku create your-app-name
```

2. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set API_KEY=your-api-key
heroku config:set TWILIO_ACCOUNT_SID=your-sid
heroku config:set TWILIO_AUTH_TOKEN=your-token
heroku config:set TWILIO_PHONE_NUMBER=your-number
heroku config:set OPENAI_API_KEY=your-openai-key
heroku config:set WHITELISTED_PHONE_NUMBERS=+1234567890
```

3. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
```

### Using Railway

1. **Connect GitHub repo to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push**

## Twilio Webhook Configuration

Configure these webhook URLs in your Twilio console:

- **Voice URL**: `https://your-domain.com/api/voice/webhook/interview/{interview_id}/`
- **Status Callback**: `https://your-domain.com/api/voice/webhook/status/`
- **Recording Callback**: `https://your-domain.com/api/voice/webhook/recording/`

## Testing with Postman

1. Import `postman/AI_Interview_Screener.postman_collection.json`
2. Import `postman/AI_Interview_Screener.postman_environment.json`
3. Update environment variables with your deployed URL and API key
4. Run the collection in sequence

## System Flow

1. **JD Processing**: Upload job description → AI generates 5-7 relevant questions
2. **Candidate Setup**: Create candidate → Upload resume → Parse skills/experience
3. **Interview Creation**: Link candidate to JD → Generate interview session
4. **Voice Call**: Trigger call → TTS asks questions → Record answers → STT transcription
5. **AI Scoring**: Evaluate answers → Calculate scores → Generate recommendation

## Architecture

- **Django REST Framework**: API backend
- **Twilio**: Voice calling and recording
- **OpenAI**: Question generation and answer scoring
- **Redis**: Celery task queue
- **PostgreSQL**: Production database (SQLite for development)

## Security Features

- API key authentication
- Phone number whitelisting (E.164 format)
- File upload validation
- CORS protection
- Input sanitization

## Data Retention

- Audio recordings: 24+ hours (configurable)
- Transcripts: Permanent
- Interview results: Permanent
- Resume files: Permanent

## Support

For issues or questions:
1. Check the logs for error details
2. Verify environment variables
3. Test Twilio webhook connectivity
4. Validate phone number format (E.164)

