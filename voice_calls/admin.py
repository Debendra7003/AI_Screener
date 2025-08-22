from django.contrib import admin
from .models import VoiceCall, CallEvent


@admin.register(VoiceCall)
class VoiceCallAdmin(admin.ModelAdmin):
    list_display = ['call_sid', 'interview', 'status', 'duration', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['call_sid', 'interview__candidate__name']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['interview']


@admin.register(CallEvent)
class CallEventAdmin(admin.ModelAdmin):
    list_display = ['voice_call', 'event_type', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['voice_call__call_sid']
    readonly_fields = ['id', 'timestamp']
    raw_id_fields = ['voice_call']
