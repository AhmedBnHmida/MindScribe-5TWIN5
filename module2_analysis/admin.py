"""
Admin configuration for the module2_analysis app.
"""
from django.contrib import admin
from .models import JournalAnalysis


@admin.register(JournalAnalysis)
class JournalAnalysisAdmin(admin.ModelAdmin):
    """
    Admin configuration for the JournalAnalysis model.
    """
    list_display = ('id', 'user', 'sentiment', 'created_at')
    list_filter = ('sentiment', 'created_at')
    search_fields = ('text', 'summary', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Content', {
            'fields': ('text', 'audio_file', 'image_file')
        }),
        ('Analysis Results', {
            'fields': ('sentiment', 'emotion_score', 'keywords', 'topics', 'summary',
                      'audio_transcription', 'image_caption', 'image_scene')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

