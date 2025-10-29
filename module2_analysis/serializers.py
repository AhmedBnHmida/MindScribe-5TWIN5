"""
Serializers for the module2_analysis app.
"""
from rest_framework import serializers
from .models import JournalAnalysis

class AnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer for multimodal analysis requests.
    Supports both FormData (with files) and JSON (with base64 data).
    """
    # Text input
    text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # File inputs (for FormData)
    audio_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    image_file = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    
    # Base64 inputs (for JSON)
    audio_data = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    audio_filename = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image_data = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image_filename = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # User ID
    user_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, data):
        """
        Check that at least one of text, audio, or image is provided.
        """
        # Clean up the data - remove None/empty values
        text = data.get('text', '').strip() if data.get('text') else ''
        audio_file = data.get('audio_file')
        image_file = data.get('image_file')
        audio_data = data.get('audio_data', '').strip() if data.get('audio_data') else ''
        image_data = data.get('image_data', '').strip() if data.get('image_data') else ''
        
        # Check if at least one meaningful input is provided
        if not text and not audio_file and not image_file and not audio_data and not image_data:
            raise serializers.ValidationError(
                "At least one of text, audio, or image must be provided."
            )
        return data


class AnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for multimodal analysis responses with enhanced fields.
    """
    sentiment = serializers.CharField()
    emotion_score = serializers.FloatField()
    emotions_detected = serializers.ListField(child=serializers.CharField(), required=False)
    keywords = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()
    detailed_summary = serializers.CharField(required=False)
    topics = serializers.ListField(child=serializers.CharField())
    positive_aspects = serializers.ListField(child=serializers.CharField(), required=False)
    negative_aspects = serializers.ListField(child=serializers.CharField(), required=False)
    action_items = serializers.ListField(child=serializers.CharField(), required=False)
    mood_analysis = serializers.CharField(required=False, allow_blank=True)
    audio_transcription = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image_caption = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image_scene = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image_analysis = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class JournalAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for the JournalAnalysis model with enhanced fields.
    """
    class Meta:
        model = JournalAnalysis
        fields = [
            'id', 'user', 'text', 'audio_file', 'image_file',
            'sentiment', 'emotion_score', 'emotions_detected', 'keywords', 'topics', 
            'summary', 'detailed_summary', 'positive_aspects', 'negative_aspects', 
            'action_items', 'mood_analysis', 'audio_transcription', 
            'image_caption', 'image_scene', 'image_analysis',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

