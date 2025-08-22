# Generated migration file for interviews app

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobDescription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('company', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField()),
                ('requirements', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='InterviewQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question_text', models.TextField()),
                ('expected_keywords', models.JSONField(blank=True, default=list)),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=10)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job_description', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='interviews.jobdescription')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('call_sid', models.CharField(blank=True, max_length=100, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('total_score', models.FloatField(blank=True, null=True)),
                ('recommendation', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='candidates.candidate')),
                ('job_description', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interviews.jobdescription')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='InterviewAnswer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transcript', models.TextField(blank=True)),
                ('audio_url', models.URLField(blank=True)),
                ('audio_duration', models.FloatField(blank=True, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
                ('interview', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interviews.interview')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interviews.interviewquestion')),
            ],
            options={
                'ordering': ['question__order'],
            },
        ),
        migrations.AddField(
            model_name='interview',
            name='questions',
            field=models.ManyToManyField(through='interviews.InterviewAnswer', to='interviews.interviewquestion'),
        ),
        migrations.AlterUniqueTogether(
            name='interviewanswer',
            unique_together={('interview', 'question')},
        ),
    ]
