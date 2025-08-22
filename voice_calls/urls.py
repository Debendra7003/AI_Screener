from django.urls import path
from . import views

urlpatterns = [
    # Twilio webhook endpoints
    path('webhook/interview/<uuid:interview_id>/', views.interview_webhook, name='interview-webhook'),
    path('webhook/next-question/<int:question_index>/', views.next_question_webhook, name='next-question-webhook'),
    path('webhook/transcription/<int:question_index>/', views.transcription_webhook, name='transcription-webhook'),
    path('webhook/status/', views.call_status_webhook, name='call-status-webhook'),
    path('webhook/recording/', views.recording_webhook, name='recording-webhook'),
]
