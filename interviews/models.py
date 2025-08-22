from django.db import models
from django.contrib.auth.models import User
import uuid


class JobDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.company}"

    class Meta:
        ordering = ['-created_at']


class InterviewQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    expected_keywords = models.JSONField(default=list, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

    class Meta:
        ordering = ['order']


class Interview(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='interviews')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    questions = models.ManyToManyField(InterviewQuestion, through='InterviewAnswer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    call_sid = models.CharField(max_length=100, blank=True, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)
    recommendation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview {self.id} - {self.candidate.name}"

    class Meta:
        ordering = ['-created_at']


class InterviewAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE)
    transcript = models.TextField(blank=True)
    audio_url = models.URLField(blank=True)
    audio_duration = models.FloatField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to {self.question.question_text[:30]}..."

    class Meta:
        unique_together = ['interview', 'question']
        ordering = ['question__order']
