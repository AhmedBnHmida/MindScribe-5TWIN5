"""
Serializers for the analysis app.
"""
from rest_framework import serializers
from .models import AnalyseIA
from journal.models import Journal

class AnalyseRequestSerializer(serializers.Serializer):
    """
    Serializer for the analysis request.
    Handles multimodal input: text, audio, and image.
    """
    text = serializers.CharField(required=False, allow_blank=True)
    audio_file = serializers.FileField(required=False, allow_null=True)
    image_file = serializers.ImageField(required=False, allow_null=True)
    user_id = serializers.CharField(required=False)
    
    def validate(self, data):
        """
        Check that at least one of text, audio_file, or image_file is provided.
        """
        if not any([data.get('text'), data.get('audio_file'), data.get('image_file')]):
            raise serializers.ValidationError(
                "At least one of text, audio_file, or image_file must be provided."
            )
        return data


class AnalyseResponseSerializer(serializers.Serializer):
    """
    Serializer for the analysis response.
    """
    sentiment = serializers.CharField()
    emotion_score = serializers.FloatField()
    keywords = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()
    topics = serializers.ListField(child=serializers.CharField())
    audio_transcription = serializers.CharField(required=False, allow_blank=True)
    image_caption = serializers.CharField(required=False, allow_blank=True)
    image_scene = serializers.CharField(required=False, allow_blank=True)


class AnalyseIASerializer(serializers.ModelSerializer):
    """
    Serializer for the AnalyseIA model.
    """
    class Meta:
        model = AnalyseIA
        fields = [
            'id', 'journal', 'mots_cles', 'ton_general', 
            'themes_detectes', 'resume_journee', 'date_analyse'
        ]
        read_only_fields = ['id', 'date_analyse']

