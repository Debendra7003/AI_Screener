from celery import shared_task
from django.utils import timezone
from .models import Interview, InterviewAnswer
from .services import AIService
import logging

logger = logging.getLogger(__name__)


@shared_task
def score_interview_async(interview_id):
    """Asynchronously score all answers for an interview"""
    try:
        interview = Interview.objects.get(id=interview_id)
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
            
        logger.info(f"Interview {interview_id} scored successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error scoring interview {interview_id}: {e}")
        return False


@shared_task
def cleanup_old_recordings():
    """Clean up old recordings and temporary files"""
    try:
        # This task can be scheduled to run daily
        # Remove recordings older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        
        # Add cleanup logic here based on your storage solution
        logger.info("Cleanup task completed")
        return True
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        return False
