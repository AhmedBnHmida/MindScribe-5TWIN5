"""
Audio analysis pipeline using Hugging Face models.
"""
import os
import logging
from transformers import pipeline, AutoProcessor, WhisperForConditionalGeneration

# Configure logging
logger = logging.getLogger(__name__)

# Global variables to store loaded models
transcription_pipeline = None

def load_models():
    """
    Load all audio analysis models.
    This function should be called once during application startup.
    """
    global transcription_pipeline
    
    logger.info("Loading audio analysis models...")
    
    try:
        # Audio transcription model
        transcription_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-small")
        logger.info("Audio transcription model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load audio transcription model: {e}")


def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file.
    
    Args:
        audio_file_path (str): The path to the audio file
        
    Returns:
        str: The transcription
    """
    if not audio_file_path or not transcription_pipeline:
        return ""
    
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            return ""
        
        # Transcribe audio
        result = transcription_pipeline(audio_file_path)
        
        return result["text"]
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return ""

