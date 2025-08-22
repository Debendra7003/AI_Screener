from django.urls import path
from . import views

urlpatterns = [
    # Candidate endpoints
    path('candidates/', views.CandidateListCreateView.as_view(), name='candidate-list'),
    path('candidates/<uuid:pk>/', views.CandidateDetailView.as_view(), name='candidate-detail'),
    path('candidates/<uuid:candidate_id>/upload-resume/', views.upload_resume, name='upload-resume'),
    
    # Candidate scoring endpoints
    path('candidate-scores/', views.CandidateScoreListView.as_view(), name='candidate-score-list'),
    path('candidate-scores/<uuid:pk>/', views.CandidateScoreDetailView.as_view(), name='candidate-score-detail'),
]
