from django.contrib import admin
from .models import Candidate, CandidateScore


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'experience_years', 'created_at']
    list_filter = ['experience_years', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'resume_file')
        }),
        ('Parsed Resume Data', {
            'fields': ('experience_years', 'skills', 'education', 'work_experience', 'summary'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CandidateScore)
class CandidateScoreAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'overall_score', 'recommendation', 'created_at']
    list_filter = ['recommendation', 'created_at']
    search_fields = ['candidate__name', 'candidate__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['candidate']
