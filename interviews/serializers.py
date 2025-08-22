from rest_framework import serializers
from .models import JobDescription, InterviewQuestion, Interview, InterviewAnswer
from candidates.models import Candidate


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'title', 'company', 'description', 'requirements', 'created_at']
        read_only_fields = ['id', 'created_at']


class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = ['id', 'question_text', 'expected_keywords', 'difficulty', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class InterviewAnswerSerializer(serializers.ModelSerializer):
    question = InterviewQuestionSerializer(read_only=True)
    
    class Meta:
        model = InterviewAnswer
        fields = ['id', 'question', 'transcript', 'audio_url', 'audio_duration', 'score', 'feedback', 'answered_at']
        read_only_fields = ['id', 'answered_at']


class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    candidate_phone = serializers.CharField(source='candidate.phone', read_only=True)
    job_title = serializers.CharField(source='job_description.title', read_only=True)
    answers = InterviewAnswerSerializer(many=True, read_only=True, source='interviewanswer_set')
    
    class Meta:
        model = Interview
        fields = [
            'id', 'candidate_name', 'candidate_phone', 'job_title', 'status', 
            'call_sid', 'started_at', 'completed_at', 'total_score', 
            'recommendation', 'created_at', 'answers'
        ]
        read_only_fields = ['id', 'created_at', 'call_sid']


class CreateInterviewSerializer(serializers.Serializer):
    candidate_id = serializers.UUIDField()
    job_description_id = serializers.UUIDField()
    
    def validate_candidate_id(self, value):
        try:
            candidate = Candidate.objects.get(id=value)
            return value
        except Candidate.DoesNotExist:
            raise serializers.ValidationError("Candidate not found")
    
    def validate_job_description_id(self, value):
        try:
            job_description = JobDescription.objects.get(id=value)
            return value
        except JobDescription.DoesNotExist:
            raise serializers.ValidationError("Job description not found")


class GenerateQuestionsSerializer(serializers.Serializer):
    job_description_text = serializers.CharField()
    num_questions = serializers.IntegerField(default=6, min_value=3, max_value=10)
