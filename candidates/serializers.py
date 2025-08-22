from rest_framework import serializers
from .models import Candidate, CandidateScore


class CandidateSerializer(serializers.ModelSerializer):
    resume_file = serializers.FileField(required=False)
    
    class Meta:
        model = Candidate
        fields = [
            'id', 'name', 'email', 'phone', 'resume_file', 
            'experience_years', 'skills', 'education', 'work_experience', 
            'summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_phone(self, value):
        """Validate phone number is in E.164 format"""
        import re
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(e164_pattern, value):
            raise serializers.ValidationError(
                "Phone number must be in E.164 format (e.g., +1234567890)"
            )
        return value


class CandidateScoreSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    
    class Meta:
        model = CandidateScore
        fields = [
            'id', 'candidate_name', 'technical_score', 'communication_score',
            'experience_score', 'overall_score', 'recommendation', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResumeUploadSerializer(serializers.Serializer):
    resume_file = serializers.FileField()
    
    def validate_resume_file(self, value):
        """Validate resume file type and size"""
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only PDF and DOCX files are allowed"
            )
        
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError(
                "File size cannot exceed 10MB"
            )
        
        return value
