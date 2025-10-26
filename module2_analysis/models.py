"""
Models for the module2_analysis app.
"""
from django.db import models
from django.conf import settings
import uuid

class JournalAnalysis(models.Model):
    """
    Model for storing multimodal journal analysis results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_analyses',
        verbose_name="User"
    )
    
    # Input content
    text = models.TextField(blank=True, verbose_name="Text content")
    audio_file = models.FileField(upload_to='journal_analyses/audio/', blank=True, null=True, verbose_name="Audio file")
    image_file = models.ImageField(upload_to='journal_analyses/images/', blank=True, null=True, verbose_name="Image file")
    
    # Text analysis results
    sentiment = models.CharField(max_length=20, blank=True, verbose_name="Sentiment")
    emotion_score = models.FloatField(default=0.5, verbose_name="Emotion score")
    emotions_detected = models.JSONField(default=list, blank=True, verbose_name="Emotions detected")
    keywords = models.JSONField(default=list, blank=True, verbose_name="Keywords")
    topics = models.JSONField(default=list, blank=True, verbose_name="Topics")
    summary = models.TextField(blank=True, verbose_name="Summary")
    detailed_summary = models.TextField(blank=True, verbose_name="Detailed summary")
    positive_aspects = models.JSONField(default=list, blank=True, verbose_name="Positive aspects")
    negative_aspects = models.JSONField(default=list, blank=True, verbose_name="Negative aspects")
    action_items = models.JSONField(default=list, blank=True, verbose_name="Action items")
    mood_analysis = models.TextField(blank=True, verbose_name="Mood analysis")
    
    # Audio analysis results
    audio_transcription = models.TextField(blank=True, verbose_name="Audio transcription")
    
    # Image analysis results
    image_caption = models.TextField(blank=True, verbose_name="Image caption")
    image_scene = models.CharField(max_length=100, blank=True, verbose_name="Image scene")
    image_analysis = models.TextField(blank=True, verbose_name="Image analysis")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    
    def __str__(self):
        return f"Analysis for {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Journal Analysis"
        verbose_name_plural = "Journal Analyses"
        ordering = ['-created_at']

