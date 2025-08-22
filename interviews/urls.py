from django.urls import path
from . import views

urlpatterns = [
    # Job Description endpoints
    path('job-descriptions/', views.JobDescriptionListCreateView.as_view(), name='job-description-list'),
    path('job-descriptions/<uuid:pk>/', views.JobDescriptionDetailView.as_view(), name='job-description-detail'),
    
    # Question generation
    path('generate-questions/', views.generate_questions, name='generate-questions'),
    
    # Interview endpoints
    path('interviews/', views.InterviewListView.as_view(), name='interview-list'),
    path('interviews/<uuid:pk>/', views.InterviewDetailView.as_view(), name='interview-detail'),
    path('interviews/create/', views.create_interview, name='create-interview'),
    path('interviews/<uuid:interview_id>/trigger/', views.trigger_interview, name='trigger-interview'),
    path('interviews/<uuid:interview_id>/results/', views.get_interview_results, name='interview-results'),
]
