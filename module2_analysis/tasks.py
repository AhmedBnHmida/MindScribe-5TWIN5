"""
Celery tasks for asynchronous processing of multimodal analysis.
Optional: Only used if Celery is configured in the project.
"""
import os
import logging
from django.conf import settings
from django.contrib.auth import get_user_model

# Try to import Celery, but don't fail if it's not installed
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    # Define a dummy decorator if Celery is not available
    def shared_task(func):
        return func
    CELERY_AVAILABLE = False

from .models import JournalAnalysis
from .services import analyze_multimodal_content

# Configure logging
logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task
def analyze_content_async(text=None, audio_path=None, image_path=None, user_id=None, analysis_id=None):
    """
    Asynchronously analyze multimodal content and save results to database.
    
    Args:
        text (str, optional): The text to analyze
        audio_path (str, optional): The path to the audio file
        image_path (str, optional): The path to the image file
        user_id (str, optional): The ID of the user
        analysis_id (str, optional): The ID of an existing JournalAnalysis to update
    
    Returns:
        dict: The analysis results
    """
    try:
        # Perform analysis
        analysis_results = analyze_multimodal_content(
            text=text,
            audio_path=audio_path,
            image_path=image_path
        )
        
        # Save results to database if user_id is provided
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                
                if analysis_id:
                    # Update existing analysis
                    journal_analysis = JournalAnalysis.objects.get(id=analysis_id)
                else:
                    # Create new analysis
                    journal_analysis = JournalAnalysis(user=user)
                
                # Update fields
                journal_analysis.text = text if text else ''
                journal_analysis.sentiment = analysis_results.get('sentiment', 'neutre')
                journal_analysis.emotion_score = analysis_results.get('emotion_score', 0.5)
                journal_analysis.keywords = analysis_results.get('keywords', [])
                journal_analysis.topics = analysis_results.get('topics', [])
                journal_analysis.summary = analysis_results.get('summary', '')
                journal_analysis.audio_transcription = analysis_results.get('audio_transcription', '')
                journal_analysis.image_caption = analysis_results.get('image_caption', '')
                journal_analysis.image_scene = analysis_results.get('image_scene', '')
                
                journal_analysis.save()
                
                # Include the analysis ID in the results
                analysis_results['analysis_id'] = str(journal_analysis.id)
                
            except User.DoesNotExist:
                logger.warning(f"User with ID {user_id} not found")
            except JournalAnalysis.DoesNotExist:
                logger.warning(f"JournalAnalysis with ID {analysis_id} not found")
            except Exception as e:
                logger.error(f"Error saving analysis to database: {e}")
        
        return analysis_results
    
    except Exception as e:
        logger.error(f"Error during async analysis: {e}")
        return {"error": str(e)}
    finally:
        # Clean up temporary files
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

