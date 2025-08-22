from django.contrib import admin
from .models import JobDescription, InterviewQuestion, Interview, InterviewAnswer


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'created_at']
    list_filter = ['created_at', 'company']
    search_fields = ['title', 'company', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'job_description', 'difficulty', 'order']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['question_text']
    readonly_fields = ['id', 'created_at']
    ordering = ['job_description', 'order']


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidate', 'job_description', 'status', 'total_score', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['candidate__name', 'candidate__email']
    readonly_fields = ['id', 'created_at', 'call_sid']
    raw_id_fields = ['candidate', 'job_description']


@admin.register(InterviewAnswer)
class InterviewAnswerAdmin(admin.ModelAdmin):
    list_display = ['interview', 'question', 'score', 'answered_at']
    list_filter = ['score', 'answered_at']
    search_fields = ['interview__candidate__name', 'question__question_text']
    readonly_fields = ['id', 'answered_at']
    raw_id_fields = ['interview', 'question']
