from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.utils import timezone
try:
    from twilio.twiml.voice_response import VoiceResponse
except ImportError:
    from twilio.twiml import VoiceResponse
from .models import VoiceCall, CallEvent
from .services import TwilioVoiceService
from interviews.models import Interview, InterviewQuestion, InterviewAnswer
from interviews.services import AIService
import json
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def interview_webhook(request, interview_id):
    """Handle Twilio webhook for interview calls"""
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        questions = InterviewQuestion.objects.filter(
            job_description=interview.job_description
        ).order_by('order')
        
        # Get current question index from request
        current_question = int(request.POST.get('current_question', 0))
        
        voice_service = TwilioVoiceService()
        question_texts = [q.question_text for q in questions]
        
        twiml = voice_service.generate_interview_twiml(question_texts, current_question)
        
        return HttpResponse(twiml, content_type='text/xml')
        
    except Exception as e:
        logger.error(f"Error in interview webhook: {e}")
        response = VoiceResponse()
        response.say("Sorry, there was an error. Please try again later.")
        response.hangup()
        return HttpResponse(str(response), content_type='text/xml')


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def next_question_webhook(request, question_index):
    """Handle moving to next question"""
    try:
        call_sid = request.POST.get('CallSid')
        recording_url = request.POST.get('RecordingUrl')
        recording_duration = request.POST.get('RecordingDuration')
        
        # Find the interview by call_sid
        voice_call = VoiceCall.objects.get(call_sid=call_sid)
        interview = voice_call.interview
        
        # Get the previous question (the one just answered)
        prev_question_index = question_index - 1
        if prev_question_index >= 0:
            questions = InterviewQuestion.objects.filter(
                job_description=interview.job_description
            ).order_by('order')
            
            if prev_question_index < len(questions):
                question = questions[prev_question_index]
                
                # Create or update answer record
                answer, created = InterviewAnswer.objects.get_or_create(
                    interview=interview,
                    question=question,
                    defaults={
                        'audio_url': recording_url,
                        'audio_duration': float(recording_duration) if recording_duration else 0,
                        'transcript': 'Transcription pending...'
                    }
                )
                
                if not created:
                    answer.audio_url = recording_url
                    answer.audio_duration = float(recording_duration) if recording_duration else 0
                    answer.save()
        
        # Generate TwiML for next question or end interview
        questions = InterviewQuestion.objects.filter(
            job_description=interview.job_description
        ).order_by('order')
        question_texts = [q.question_text for q in questions]
        
        voice_service = TwilioVoiceService()
        twiml = voice_service.generate_interview_twiml(question_texts, question_index)
        
        # If this was the last question, mark interview as completed
        if question_index >= len(question_texts):
            interview.status = 'completed'
            interview.completed_at = timezone.now()
            interview.save()
            
            # Trigger scoring process (could be done asynchronously)
            score_interview_answers(interview)
        
        return HttpResponse(twiml, content_type='text/xml')
        
    except Exception as e:
        logger.error(f"Error in next question webhook: {e}")
        response = VoiceResponse()
        response.say("Thank you for your time. The interview is now complete.")
        response.hangup()
        return HttpResponse(str(response), content_type='text/xml')


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def transcription_webhook(request, question_index):
    """Handle transcription webhook from Twilio"""
    try:
        call_sid = request.POST.get('CallSid')
        transcription_text = request.POST.get('TranscriptionText', '')
        
        # Find the interview and question
        voice_call = VoiceCall.objects.get(call_sid=call_sid)
        interview = voice_call.interview
        
        questions = InterviewQuestion.objects.filter(
            job_description=interview.job_description
        ).order_by('order')
        
        if question_index < len(questions):
            question = questions[question_index]
            
            # Update answer with transcription
            answer = InterviewAnswer.objects.filter(
                interview=interview,
                question=question
            ).first()
            
            if answer:
                answer.transcript = transcription_text
                answer.save()
                
                # Score the answer using AI
                ai_service = AIService()
                score_data = ai_service.score_answer(
                    question.question_text,
                    transcription_text,
                    question.expected_keywords
                )
                
                answer.score = score_data.get('score', 0)
                answer.feedback = score_data.get('feedback', '')
                answer.save()
        
        return HttpResponse('OK')
        
    except Exception as e:
        logger.error(f"Error in transcription webhook: {e}")
        return HttpResponse('Error', status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def call_status_webhook(request):
    """Handle call status updates from Twilio"""
    try:
        call_sid = request.POST.get('CallSid')
        call_status = request.POST.get('CallStatus')
        
        # Update voice call status
        voice_call = VoiceCall.objects.filter(call_sid=call_sid).first()
        if voice_call:
            voice_call.status = call_status.lower()
            
            if call_status in ['completed', 'failed', 'no-answer', 'busy']:
                voice_call.ended_at = timezone.now()
                
                # Update interview status
                if call_status == 'completed':
                    voice_call.interview.status = 'completed'
                else:
                    voice_call.interview.status = 'failed'
                voice_call.interview.save()
            
            voice_call.save()
            
            # Create call event
            CallEvent.objects.create(
                voice_call=voice_call,
                event_type=f'call_{call_status.lower()}',
                event_data=dict(request.POST)
            )
        
        return HttpResponse('OK')
        
    except Exception as e:
        logger.error(f"Error in call status webhook: {e}")
        return HttpResponse('Error', status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def recording_webhook(request):
    """Handle recording availability webhook from Twilio"""
    try:
        call_sid = request.POST.get('CallSid')
        recording_url = request.POST.get('RecordingUrl')
        recording_sid = request.POST.get('RecordingSid')
        recording_duration = request.POST.get('RecordingDuration')
        
        # Update voice call with recording info
        voice_call = VoiceCall.objects.filter(call_sid=call_sid).first()
        if voice_call:
            voice_call.recording_url = recording_url
            voice_call.recording_sid = recording_sid
            voice_call.duration = int(recording_duration) if recording_duration else 0
            voice_call.save()
            
            # Create call event
            CallEvent.objects.create(
                voice_call=voice_call,
                event_type='recording_available',
                event_data={
                    'recording_url': recording_url,
                    'recording_sid': recording_sid,
                    'duration': recording_duration
                }
            )
        
        return HttpResponse('OK')
        
    except Exception as e:
        logger.error(f"Error in recording webhook: {e}")
        return HttpResponse('Error', status=500)


def score_interview_answers(interview):
    """Score all answers for an interview and generate final recommendation"""
    try:
        answers = InterviewAnswer.objects.filter(interview=interview)
        total_score = 0
        scored_answers = 0
        
        ai_service = AIService()
        
        for answer in answers:
            if answer.score is None and answer.transcript:
                # Score the answer
                score_data = ai_service.score_answer(
                    answer.question.question_text,
                    answer.transcript,
                    answer.question.expected_keywords
                )
                
                answer.score = score_data.get('score', 0)
                answer.feedback = score_data.get('feedback', '')
                answer.save()
            
            if answer.score is not None:
                total_score += answer.score
                scored_answers += 1
        
        # Calculate average score
        if scored_answers > 0:
            interview.total_score = total_score / scored_answers
            
            # Generate final recommendation
            interview_data = {
                'candidate_name': interview.candidate.name,
                'total_score': interview.total_score,
                'individual_scores': [a.score for a in answers if a.score],
                'qa_summary': '\n'.join([
                    f"Q: {a.question.question_text}\nA: {a.transcript[:200]}..."
                    for a in answers if a.transcript
                ])
            }
            
            interview.recommendation = ai_service.generate_final_recommendation(interview_data)
            interview.save()
            
    except Exception as e:
        logger.error(f"Error scoring interview: {e}")
