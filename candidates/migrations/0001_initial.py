# Generated migration file for candidates app

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(help_text='E.164 format (e.g., +1234567890)', max_length=20)),
                ('resume_file', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('experience_years', models.PositiveIntegerField(blank=True, null=True)),
                ('skills', models.JSONField(blank=True, default=list)),
                ('education', models.JSONField(blank=True, default=list)),
                ('work_experience', models.JSONField(blank=True, default=list)),
                ('summary', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CandidateScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('technical_score', models.FloatField(default=0.0)),
                ('communication_score', models.FloatField(default=0.0)),
                ('experience_score', models.FloatField(default=0.0)),
                ('overall_score', models.FloatField(default=0.0)),
                ('recommendation', models.CharField(choices=[('hire', 'Hire'), ('maybe', 'Maybe'), ('reject', 'Reject')], default='maybe', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='score', to='candidates.candidate')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='candidate',
            unique_together={('email', 'phone')},
        ),
    ]
