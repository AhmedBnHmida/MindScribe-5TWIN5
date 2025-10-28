import os
import logging
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import AnalyseRequestSerializer, AnalyseResponseSerializer, AnalyseIASerializer
from .models import AnalyseIA
from journal.models import Journal
from .ai_services import analyze_multimodal_content

# Configure logging
logger = logging.getLogger(__name__)

User = get_user_model()

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def analyse_api_view(request):
    """
    API view for multimodal analysis.
    
    POST: Analyze text, audio, and/or image content
    """
    serializer = AnalyseRequestSerializer(data=request.data)
    
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
        response_serializer = AnalyseResponseSerializer(data=analysis_results)
        if response_serializer.is_valid():
            # If user_id is provided, save the analysis to the database
            if user_id:
                try:
                    # Try to get the user
                    user = User.objects.get(id=user_id)
                    
                    # Create a journal entry if needed
                    journal_type = 'texte'
                    if audio_file and not text and not image_file:
                        journal_type = 'audio'
                    elif image_file and not text and not audio_file:
                        journal_type = 'image'
                    
                    journal = Journal.objects.create(
                        utilisateur=user,
                        contenu_texte=text if text else '',
                        type_entree=journal_type
                    )
                    
                    # Save audio and image if provided
                    if audio_file:
                        journal.audio = audio_file
                    
                    if image_file:
                        journal.image = image_file
                    
                    journal.save()
                    
                    # Create analysis entry
                    analyse = AnalyseIA.objects.create(
                        journal=journal,
                        mots_cles=analysis_results.get('keywords', []),
                        ton_general=analysis_results.get('sentiment', 'neutre'),
                        themes_detectes=analysis_results.get('topics', []),
                        resume_journee=analysis_results.get('summary', '')
                    )
                    
                    # Include the analysis ID in the response
                    analysis_results['analyse_id'] = str(analyse.id)
                
                except User.DoesNotExist:
                    logger.warning(f"User with ID {user_id} not found")
                except Exception as e:
                    logger.error(f"Error saving analysis to database: {e}")
            
            return Response(analysis_results, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return Response(
            {"error": "An error occurred during analysis."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        # Clean up temporary files
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


class AnalyseAPIView(APIView):
    """
    API view for multimodal analysis (class-based version).
    This is kept for reference but not used.
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny]