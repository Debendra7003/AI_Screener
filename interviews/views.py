from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import JobDescription, InterviewQuestion, Interview, InterviewAnswer
from .serializers import (
    JobDescriptionSerializer, InterviewQuestionSerializer, 
    InterviewSerializer, CreateInterviewSerializer, GenerateQuestionsSerializer
)
from .services import AIService
from candidates.models import Candidate
from voice_calls.services import TwilioVoiceService
from voice_calls.models import VoiceCall
import logging

logger = logging.getLogger(__name__)


class JobDescriptionListCreateView(generics.ListCreateAPIView):
    """Create job descriptions and generate questions"""
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.AllowAny]


class JobDescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete job descriptions"""
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def generate_questions(request):
    """Generate interview questions from job description"""
    serializer = GenerateQuestionsSerializer(data=request.data)
    
    if serializer.is_valid():
        job_description_text = serializer.validated_data['job_description_text']
        num_questions = serializer.validated_data['num_questions']
        
        try:
            # Create job description
            job_desc = JobDescription.objects.create(
                title="Generated JD",
                description=job_description_text
            )
            
            # Generate questions using AI
            ai_service = AIService()
            questions_data = ai_service.generate_questions_from_jd(
                job_description_text, num_questions
            )
            
            # Save questions to database
            questions = []
            for i, q_data in enumerate(questions_data):
                question = InterviewQuestion.objects.create(
                    job_description=job_desc,
                    question_text=q_data.get('question', ''),
                    expected_keywords=q_data.get('expected_keywords', []),
                    difficulty=q_data.get('difficulty', 'medium'),
                    order=i + 1
                )
                questions.append(question)
            
            return Response({
                'job_description_id': job_desc.id,
                'questions': InterviewQuestionSerializer(questions, many=True).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return Response(
                {'error': 'Failed to generate questions'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewListView(generics.ListAPIView):
    """List all interviews"""
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [permissions.AllowAny]


class InterviewDetailView(generics.RetrieveAPIView):
    """Get interview details with results"""
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_interview(request):
    """Create and trigger an interview"""
    serializer = CreateInterviewSerializer(data=request.data)
    
    if serializer.is_valid():
        candidate_id = serializer.validated_data['candidate_id']
        job_description_id = serializer.validated_data['job_description_id']
        
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            job_description = get_object_or_404(JobDescription, id=job_description_id)
            
            # Create interview
            interview = Interview.objects.create(
                candidate=candidate,
                job_description=job_description,
                status='pending'
            )
            
            return Response({
                'interview_id': interview.id,
                'message': 'Interview created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating interview: {e}")
            return Response(
                {'error': 'Failed to create interview'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def trigger_interview(request, interview_id):
    """Trigger notification call for interview"""
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        
        if interview.status != 'pending':
            return Response(
                {'error': 'Interview is not in pending status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate candidate phone number
        voice_service = TwilioVoiceService()
        if not voice_service.validate_phone_number(interview.candidate.phone):
            return Response(
                {'error': f'Phone number {interview.candidate.phone} is not valid or whitelisted'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initiate simple notification call
        call_result = voice_service.initiate_simple_notification_call(
            interview.candidate.phone,
            interview.candidate.name
        )
        
        # Create voice call record
        voice_call = VoiceCall.objects.create(
            interview=interview,
            phone_number=interview.candidate.phone,
            call_sid=call_result['call_sid'],
            status='initiated'
        )
        
        # Update interview status
        interview.status = 'in_progress'
        interview.started_at = timezone.now()
        interview.save()
        
        return Response({
            'message': 'Notification call initiated successfully',
            'call_sid': call_result['call_sid'],
            'interview_id': interview.id,
            'status': 'notification_sent'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        logger.error(f"Error triggering interview: {e}")
        return Response(
            {'error': 'Failed to trigger interview'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_interview_results(request, interview_id):
    """Get complete interview results"""
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        
        # Get all answers
        answers = InterviewAnswer.objects.filter(interview=interview).order_by('question__order')
        
        results = {
            'interview_id': interview.id,
            'candidate': {
                'name': interview.candidate.name,
                'email': interview.candidate.email,
                'phone': interview.candidate.phone
            },
            'job_description': {
                'title': interview.job_description.title,
                'company': interview.job_description.company
            },
            'status': interview.status,
            'total_score': interview.total_score,
            'recommendation': interview.recommendation,
            'started_at': interview.started_at,
            'completed_at': interview.completed_at,
            'questions_and_answers': []
        }
        
        for answer in answers:
            results['questions_and_answers'].append({
                'question': answer.question.question_text,
                'transcript': answer.transcript,
                'audio_url': answer.audio_url,
                'audio_duration': answer.audio_duration,
                'score': answer.score,
                'feedback': answer.feedback,
                'answered_at': answer.answered_at
            })
        
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting interview results: {e}")
        return Response(
            {'error': 'Failed to get interview results'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
