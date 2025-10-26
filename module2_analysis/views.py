"""
Views for the module2_analysis app.
"""
import os
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import JournalAnalysis
from .serializers import AnalysisRequestSerializer, AnalysisResponseSerializer, JournalAnalysisSerializer
from .services import analyze_multimodal_content

# Configure logging
logger = logging.getLogger(__name__)

User = get_user_model()

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def analyse_api_view(request):
    """
    API endpoint for multimodal analysis.
    
    Accepts text, audio, and/or image content and returns analysis results.
    
    POST:
        - text: optional string
        - audio_file: optional file (mp3, wav)
        - image_file: optional file (jpg, png)
        - user_id: optional string (user ID for saving results)
    
    Returns:
        JSON with analysis results
    """
    serializer = AnalysisRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract data from request
    text = serializer.validated_data.get('text', '')
    audio_file = serializer.validated_data.get('audio_file')
    image_file = serializer.validated_data.get('image_file')
    user_id = serializer.validated_data.get('user_id')
    
    # Initialize paths to None
    audio_path = None
    image_path = None
    
    # Save files if provided
    if audio_file:
        # Create media directory if it doesn't exist
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp_analysis'), exist_ok=True)
        
        # Save audio file
        audio_path = os.path.join(settings.MEDIA_ROOT, 'temp_analysis', audio_file.name)
        with open(audio_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
    
    if image_file:
        # Create media directory if it doesn't exist
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp_analysis'), exist_ok=True)
        
        # Save image file
        image_path = os.path.join(settings.MEDIA_ROOT, 'temp_analysis', image_file.name)
        with open(image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
    
    try:
        # Perform analysis
        analysis_results = analyze_multimodal_content(
            text=text,
            audio_path=audio_path,
            image_path=image_path
        )
        
        # Validate response data
        response_serializer = AnalysisResponseSerializer(data=analysis_results)
        if response_serializer.is_valid():
            # If user_id is provided, save the analysis to the database
            if user_id:
                try:
                    # Try to get the user
                    user = User.objects.get(id=user_id)
                    
                    # Create a journal analysis entry with enhanced fields
                    journal_analysis = JournalAnalysis.objects.create(
                        user=user,
                        text=text if text else '',
                        sentiment=analysis_results.get('sentiment', 'neutre'),
                        emotion_score=analysis_results.get('emotion_score', 0.5),
                        emotions_detected=analysis_results.get('emotions_detected', []),
                        keywords=analysis_results.get('keywords', []),
                        topics=analysis_results.get('topics', []),
                        summary=analysis_results.get('summary', ''),
                        detailed_summary=analysis_results.get('detailed_summary', ''),
                        positive_aspects=analysis_results.get('positive_aspects', []),
                        negative_aspects=analysis_results.get('negative_aspects', []),
                        action_items=analysis_results.get('action_items', []),
                        mood_analysis=analysis_results.get('mood_analysis', ''),
                        audio_transcription=analysis_results.get('audio_transcription', ''),
                        image_caption=analysis_results.get('image_caption', ''),
                        image_scene=analysis_results.get('image_scene', ''),
                        image_analysis=analysis_results.get('image_analysis', '')
                    )
                    
                    # Save audio and image if provided
                    if audio_file:
                        journal_analysis.audio_file = audio_file
                    
                    if image_file:
                        journal_analysis.image_file = image_file
                    
                    journal_analysis.save()
                    
                    # Include the analysis ID in the response
                    analysis_results['analysis_id'] = str(journal_analysis.id)
                
                except User.DoesNotExist:
                    logger.warning(f"User with ID {user_id} not found")
                except Exception as e:
                    logger.error(f"Error saving analysis to database: {e}")
            
            return Response(analysis_results, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        error_message = str(e)
        if "Error in AI analysis:" in error_message:
            # This is an error from our AI service, return it directly
            return Response(
                {"error": error_message},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        else:
            # This is some other error
            return Response(
                {"error": f"An error occurred during analysis: {error_message}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    finally:
        # Clean up temporary files
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


class JournalAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JournalAnalysis model.
    
    Provides CRUD operations for journal analyses.
    """
    queryset = JournalAnalysis.objects.all()
    serializer_class = JournalAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset to only return analyses for the current user.
        """
        return JournalAnalysis.objects.filter(user=self.request.user)

