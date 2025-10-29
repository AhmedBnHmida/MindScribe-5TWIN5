"""
Views for the module2_analysis app.
"""
import os
import base64
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
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
    # Log incoming data for debugging
    print("="*80)
    print("ANALYSE API VIEW CALLED")
    print(f"Content-Type: {request.content_type}")
    print(f"Request method: {request.method}")
    print(f"Request POST keys: {list(request.POST.keys())}")
    print(f"Request FILES keys: {list(request.FILES.keys())}")
    
    # Try to access request.data carefully
    try:
        print(f"Request data keys: {list(request.data.keys())}")
        print(f"Request data dict: {dict(request.data)}")
    except Exception as e:
        print(f"Error accessing request.data: {e}")
    
    print("="*80)
    
    # Combine POST and FILES data for multipart requests
    data = {}
    if request.content_type and 'multipart/form-data' in request.content_type:
        # For multipart/form-data, use POST and FILES
        data.update(request.POST.dict())
        data.update(request.FILES)
        print(f"Using POST+FILES data: {list(data.keys())}")
    else:
        # For JSON or other types, use request.data
        data = request.data
        print(f"Using request.data: {list(data.keys())}")
    
    serializer = AnalysisRequestSerializer(data=data)
    
    if not serializer.is_valid():
        print(f"VALIDATION FAILED: {serializer.errors}")
        print(f"Data passed to serializer: {data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract data from request
    text = serializer.validated_data.get('text', '')
    user_id = serializer.validated_data.get('user_id')
    
    # Handle audio (either file or base64)
    audio_file = serializer.validated_data.get('audio_file')
    audio_data = serializer.validated_data.get('audio_data')
    audio_filename = serializer.validated_data.get('audio_filename', 'audio.wav')
    
    # Handle image (either file or base64)
    image_file = serializer.validated_data.get('image_file')
    image_data = serializer.validated_data.get('image_data')
    image_filename = serializer.validated_data.get('image_filename', 'image.jpg')
    
    # Convert base64 to files if needed
    if audio_data and not audio_file:
        try:
            audio_bytes = base64.b64decode(audio_data)
            audio_file = ContentFile(audio_bytes, name=audio_filename)
            print(f"Converted base64 audio to file: {audio_filename}, size: {len(audio_bytes)} bytes")
        except Exception as e:
            print(f"Error decoding audio base64: {e}")
            return Response({"error": "Invalid audio data"}, status=status.HTTP_400_BAD_REQUEST)
    
    if image_data and not image_file:
        try:
            image_bytes = base64.b64decode(image_data)
            image_file = ContentFile(image_bytes, name=image_filename)
            print(f"Converted base64 image to file: {image_filename}, size: {len(image_bytes)} bytes")
        except Exception as e:
            print(f"Error decoding image base64: {e}")
            return Response({"error": "Invalid image data"}, status=status.HTTP_400_BAD_REQUEST)
    
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
        
        # Debug logging for response validation
        print(f"Validating response with serializer: {analysis_results.keys()}")
        
        if response_serializer.is_valid():
            print("Response serializer validation successful")
            # If user_id is provided, save the analysis to the database
            if user_id:
                try:
                    # Try to get the user
                    print(f"Looking up user with ID: {user_id}")
                    user = User.objects.get(id=user_id)
                    print(f"Found user: {user.username}")
                    
                    # Handle None values for JSONFields
                    emotions_detected = analysis_results.get('emotions_detected') or []
                    keywords = analysis_results.get('keywords') or []
                    topics = analysis_results.get('topics') or []
                    positive_aspects = analysis_results.get('positive_aspects') or []
                    negative_aspects = analysis_results.get('negative_aspects') or []
                    action_items = analysis_results.get('action_items') or []
                    
                    print("Creating journal analysis entry")
                    # Create a journal analysis entry with enhanced fields
                    journal_analysis = JournalAnalysis.objects.create(
                        user=user,
                        text=text if text else '',
                        sentiment=analysis_results.get('sentiment', 'neutre'),
                        emotion_score=analysis_results.get('emotion_score', 0.5),
                        emotions_detected=emotions_detected,
                        keywords=keywords,
                        topics=topics,
                        summary=analysis_results.get('summary', ''),
                        detailed_summary=analysis_results.get('detailed_summary', ''),
                        positive_aspects=positive_aspects,
                        negative_aspects=negative_aspects,
                        action_items=action_items,
                        mood_analysis=analysis_results.get('mood_analysis', ''),
                        audio_transcription=analysis_results.get('audio_transcription') or '',
                        image_caption=analysis_results.get('image_caption') or '',
                        image_scene=analysis_results.get('image_scene') or '',
                        image_analysis=analysis_results.get('image_analysis') or ''
                    )
                    
                    print("Journal analysis entry created successfully")
                    
                    # Save audio and image if provided
                    if audio_file:
                        print(f"Saving audio file: {audio_file.name}")
                        journal_analysis.audio_file = audio_file
                    
                    if image_file:
                        print(f"Saving image file: {image_file.name}")
                        journal_analysis.image_file = image_file
                    
                    journal_analysis.save()
                    print("D")
                    
                    # Include the analysis ID in the response
                    analysis_results['analysis_id'] = str(journal_analysis.id)
                    print(f"Analysis ID added to response: {journal_analysis.id}")
                
                except User.DoesNotExist:
                    logger.warning(f"User with ID {user_id} not found")
                    print(f"ERROR: User with ID {user_id} not found")
                except Exception as e:
                    logger.error(f"Error saving analysis to database: {e}")
                    print(f"ERROR saving analysis to database: {e}")
                    print(f"Error type: {type(e)}")
                    # Return error to client for debugging
                    return Response(
                        {"error": f"Database error: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            print("Returning successful response")
            return Response(analysis_results, status=status.HTTP_200_OK)
        else:
            print(f"Response serializer validation failed: {response_serializer.errors}")
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        error_message = str(e)
        
        # Return all errors directly to the client
        return Response(
            {"error": error_message},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    finally:
        # Clean up temporary files
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_detail_view(request, analysis_id):
    """
    View for displaying a single analysis in detail.
    """
    from django.shortcuts import render, get_object_or_404
    
    analysis = get_object_or_404(JournalAnalysis, id=analysis_id, user=request.user)
    return render(request, 'journal/analysis_detail.html', {'analysis': analysis})


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

