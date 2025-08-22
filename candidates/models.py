from django.db import models
import uuid


class Candidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, help_text="E.164 format (e.g., +1234567890)")
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # Parsed resume data
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    skills = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    work_experience = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['email', 'phone']


class CandidateScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='score')
    technical_score = models.FloatField(default=0.0)
    communication_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    recommendation = models.CharField(
        max_length=20,
        choices=[
            ('hire', 'Hire'),
            ('maybe', 'Maybe'),
            ('reject', 'Reject'),
        ],
        default='maybe'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Score for {self.candidate.name}: {self.overall_score}"
