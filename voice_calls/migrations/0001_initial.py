# Generated migration file for voice_calls app

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoiceCall',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('call_sid', models.CharField(max_length=100, unique=True)),
                ('to_phone', models.CharField(max_length=20)),
                ('from_phone', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('initiated', 'Initiated'), ('ringing', 'Ringing'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed'), ('no_answer', 'No Answer'), ('busy', 'Busy')], default='initiated', max_length=20)),
                ('duration', models.PositiveIntegerField(blank=True, help_text='Duration in seconds', null=True)),
                ('recording_url', models.URLField(blank=True)),
                ('recording_sid', models.CharField(blank=True, max_length=100)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('interview', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='voice_call', to='interviews.interview')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CallEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(choices=[('call_initiated', 'Call Initiated'), ('call_ringing', 'Call Ringing'), ('call_answered', 'Call Answered'), ('call_completed', 'Call Completed'), ('recording_available', 'Recording Available'), ('transcription_available', 'Transcription Available')], max_length=30)),
                ('event_data', models.JSONField(default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('voice_call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='voice_calls.voicecall')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
