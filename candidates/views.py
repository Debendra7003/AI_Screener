from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Candidate, CandidateScore
from .serializers import CandidateSerializer, CandidateScoreSerializer, ResumeUploadSerializer
from .services import ResumeParserService
import os
import logging

logger = logging.getLogger(__name__)


class CandidateListCreateView(generics.ListCreateAPIView):
    """List and create candidates"""
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.AllowAny]


class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete candidates"""
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def upload_resume(request, candidate_id):
    """Upload and parse resume for a candidate"""
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response(
            {'error': 'Candidate not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ResumeUploadSerializer(data=request.data)
    
    if serializer.is_valid():
        resume_file = serializer.validated_data['resume_file']
        
        try:
            # Save file
            file_name = f"resumes/{candidate_id}_{resume_file.name}"
            file_path = default_storage.save(file_name, ContentFile(resume_file.read()))
            full_path = default_storage.path(file_path)
            
            # Parse resume
            parser = ResumeParserService()
            file_extension = os.path.splitext(resume_file.name)[1][1:]  # Remove the dot
            parsed_data = parser.parse_resume(full_path, file_extension)
            
            # Update candidate with parsed data
            candidate.resume_file = file_path
            candidate.experience_years = parsed_data.get('experience_years', 0)
            candidate.skills = parsed_data.get('skills', [])
            candidate.education = parsed_data.get('education', [])
            candidate.work_experience = parsed_data.get('work_experience', [])
            candidate.summary = parsed_data.get('summary', '')
            candidate.save()
            
            return Response({
                'message': 'Resume uploaded and parsed successfully',
                'parsed_data': parsed_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            return Response(
                {'error': 'Failed to process resume'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidateScoreListView(generics.ListAPIView):
    """List candidate scores"""
    queryset = CandidateScore.objects.all()
    serializer_class = CandidateScoreSerializer
    permission_classes = [permissions.AllowAny]


class CandidateScoreDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update candidate scores"""
    queryset = CandidateScore.objects.all()
    serializer_class = CandidateScoreSerializer
    permission_classes = [permissions.AllowAny]
