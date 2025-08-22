# AI Interview Screener - Design Document

## System Overview

The AI Interview Screener is a comprehensive backend system that automates the technical interview process through voice calls, AI-powered question generation, real-time transcription, and intelligent scoring.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/API    │    │  Django REST    │    │   External      │
│   (Postman)     │◄──►│   Framework     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ├─ Twilio (Voice)
                       ┌─────────────────┐             ├─ OpenAI (AI)
                       │   PostgreSQL    │             └─ Redis (Queue)
                       │   Database      │
                       └─────────────────┘
```

### Component Architecture

1. **API Layer**: Django REST Framework with API key authentication
2. **Business Logic**: Service classes for AI, voice, and resume processing
3. **Data Layer**: PostgreSQL with Django ORM
4. **External Integrations**: Twilio, OpenAI, Redis
5. **Background Tasks**: Celery for async processing

## Data Design

### Core Entities

#### JobDescription
- Stores job requirements and descriptions
- Links to generated interview questions
- Supports multiple companies and roles

#### Candidate
- Personal information with E.164 phone validation
- Parsed resume data (skills, experience, education)
- File storage for resume uploads

#### Interview
- Links candidate to job description
- Tracks call status and timing
- Stores final scores and recommendations

#### InterviewQuestion
- AI-generated questions based on JD
- Expected keywords for scoring
- Difficulty levels and ordering

#### InterviewAnswer
- Audio recordings and transcripts
- AI-generated scores and feedback
- Timing and duration tracking

#### VoiceCall
- Twilio call management
- Status tracking and webhooks
- Recording URLs and metadata

## AI Usage Points

### 1. Question Generation
- **Input**: Job description text
- **Process**: OpenAI GPT-3.5 analyzes JD and generates relevant questions
- **Output**: 5-7 structured questions with keywords and difficulty levels
- **Fallback**: Predefined question bank if AI fails

### 2. Answer Scoring
- **Input**: Question, candidate answer transcript, expected keywords
- **Process**: AI evaluates relevance, technical accuracy, communication clarity
- **Output**: Numerical score (0-10) with detailed feedback
- **Criteria**: Technical skills, problem-solving, communication

### 3. Final Recommendation
- **Input**: All interview answers and scores
- **Process**: Holistic evaluation of candidate performance
- **Output**: Hire/Maybe/Reject recommendation with reasoning
- **Factors**: Overall score, consistency, specific strengths/weaknesses

## System Flow

### Complete Interview Process

```
1. JD Upload → AI Question Generation → Questions Stored
                     ↓
2. Candidate Creation → Resume Upload → Data Parsing
                     ↓
3. Interview Creation → Link Candidate + JD
                     ↓
4. Call Trigger → Twilio Outbound Call → TTS Questions
                     ↓
5. Answer Recording → STT Transcription → AI Scoring
                     ↓
6. Final Scoring → AI Recommendation → Results Available
```

### Webhook Flow

```
Twilio Call Events → Django Webhooks → Database Updates
                                   ↓
Recording Available → Transcription → AI Scoring → Final Results
```
