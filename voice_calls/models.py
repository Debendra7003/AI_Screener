from django.db import models
import uuid


class VoiceCall(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.OneToOneField('interviews.Interview', on_delete=models.CASCADE, related_name='voice_call')
    call_sid = models.CharField(max_length=100, unique=True)
    to_phone = models.CharField(max_length=20)
    from_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in seconds")
    recording_url = models.URLField(blank=True)
    recording_sid = models.CharField(max_length=100, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Call {self.call_sid} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class CallEvent(models.Model):
    EVENT_TYPES = [
        ('call_initiated', 'Call Initiated'),
        ('call_ringing', 'Call Ringing'),
        ('call_answered', 'Call Answered'),
        ('call_completed', 'Call Completed'),
        ('recording_available', 'Recording Available'),
        ('transcription_available', 'Transcription Available'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voice_call = models.ForeignKey(VoiceCall, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.voice_call.call_sid}"

    class Meta:
        ordering = ['-timestamp']
