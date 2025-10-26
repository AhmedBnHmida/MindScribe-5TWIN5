"""
Main AI orchestration layer for multimodal analysis.
This module uses OpenRouter to access Mistral AI for multimodal analysis.
"""
import os
import logging
import json
import requests
import base64
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# OpenRouter API key
OPENROUTER_API_KEY = ""

# No need for load_all_models function since we're using OpenRouter API


def analyze_multimodal_content(text=None, audio_path=None, image_path=None):
    """
    Analyze multimodal content (text, audio, image) using Mistral AI via OpenRouter.
    
    Args:
        text (str, optional): The text to analyze
        audio_path (str, optional): The path to the audio file
        image_path (str, optional): The path to the image file
        
    Returns:
        dict: A dictionary containing the analysis results
    """
    logger.info(f"Analyzing content: text={bool(text)}, audio={bool(audio_path)}, image={bool(image_path)}")
    
    # Prepare the content for analysis
    content_parts = []
    
    # Add text content if provided
    if text:
        content_parts.append(f"TEXT CONTENT: {text}")
    
    # Process audio file if provided
    if audio_path:
        content_parts.append(f"AUDIO FILE: {os.path.basename(audio_path)}")
    
    # Process image file if provided
    if image_path:
        content_parts.append(f"IMAGE FILE: {os.path.basename(image_path)}")
    
    # Combine all content
    combined_content = "\n\n".join(content_parts)
    
    # If no content provided, return a default message with enhanced structure
    if not combined_content:
        return {
            "sentiment": "neutre",
            "emotion_score": 0.5,
            "emotions_detected": ["calme", "neutre"],
            "keywords": ["analyse", "journal", "contenu"],
            "summary": "Pas de contenu à analyser.",
            "detailed_summary": "Aucun contenu n'a été fourni pour l'analyse. Tu peux ajouter du texte, un enregistrement audio ou une image pour obtenir une analyse détaillée.",
            "topics": ["journal", "analyse"],
            "positive_aspects": [],
            "negative_aspects": [],
            "action_items": ["Ajouter du contenu pour obtenir une analyse"],
            "mood_analysis": "Aucune analyse d'humeur disponible sans contenu.",
            "audio_transcription": "",
            "image_caption": "",
            "image_scene": "",
            "image_analysis": ""
        }
    
    # Create an enhanced prompt with more detailed analysis requirements
    prompt = f"""Analyze the following content and provide a detailed structured analysis in French:

{combined_content}

Please provide the following information in a structured JSON format:
{{
  "sentiment": "positif/neutre/negatif",
  "emotion_score": 0.0-1.0,
  "emotions_detected": ["emotion1", "emotion2", "emotion3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "summary": "A clear and concise summary of the content that captures the essence of the day",
  "detailed_summary": "A more detailed summary with key insights from the content",
  "topics": ["topic1", "topic2", "topic3"],
  "positive_aspects": ["positive aspect 1", "positive aspect 2", "positive aspect 3"],
  "negative_aspects": ["negative aspect 1", "negative aspect 2", "negative aspect 3"],
  "action_items": ["potential action item 1", "potential action item 2"],
  "mood_analysis": "A brief analysis of the overall mood and emotional state",
  "audio_transcription": "transcription if audio file is provided",
  "image_caption": "caption if image is provided",
  "image_scene": "scene type if image is provided",
  "image_analysis": "deeper analysis of what the image represents in context"
}}

IMPORTANT: 
1. Respond ONLY with the JSON object, no additional text.
2. Make the summary clear, concise and personal (using "tu" form).
3. For positive and negative aspects, identify specific elements from the content.
4. For action items, suggest potential follow-up actions based on the content.
5. Ensure all analysis is in French and written in a supportive, empathetic tone.
"""
    
    try:
        # Call DeepSeek model via OpenRouter direct API - WAIT for the response
        logger.info("Sending request to DeepSeek AI...")
        
        # Prepare the request payload exactly as provided
        payload = {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": [
                {"role": "system", "content": "You are an AI assistant that analyzes text, audio, and images. You always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Make the API request using the exact format provided
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mindscribe-journal.com",
                "X-Title": "MindScribe Journal"
            },
            data=json.dumps(payload)
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        ai_response = response_data["choices"][0]["message"]["content"]
        logger.info(f"Received response from DeepSeek AI")
        print(f"Raw response from DeepSeek AI: {ai_response}")
        
        # Clean up the response - remove markdown code blocks if present
        if ai_response.startswith("```") and "```" in ai_response[3:]:
            # Extract the JSON content from markdown code blocks
            ai_response = ai_response.split("```", 2)[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
            ai_response = ai_response.strip()
            
        # Parse JSON response
        ai_results = json.loads(ai_response)
        logger.info(f"Successfully parsed JSON from DeepSeek AI")
        
        # Create the enhanced result with values from the AI response
        results = {
            "sentiment": ai_results.get("sentiment", "neutre"),
            "emotion_score": ai_results.get("emotion_score", 0.5),
            "emotions_detected": ai_results.get("emotions_detected", ["calme", "neutre"]),
            "keywords": ai_results.get("keywords", ["analyse", "journal", "contenu"]),
            "summary": ai_results.get("summary", "Analyse du contenu en cours..."),
            "detailed_summary": ai_results.get("detailed_summary", "Une analyse détaillée est en cours de génération..."),
            "topics": ai_results.get("topics", ["journal", "analyse"]),
            "positive_aspects": ai_results.get("positive_aspects", []),
            "negative_aspects": ai_results.get("negative_aspects", []),
            "action_items": ai_results.get("action_items", []),
            "mood_analysis": ai_results.get("mood_analysis", "Analyse d'humeur en cours..."),
            "audio_transcription": ai_results.get("audio_transcription", ""),
            "image_caption": ai_results.get("image_caption", ""),
            "image_scene": ai_results.get("image_scene", ""),
            "image_analysis": ai_results.get("image_analysis", "")
        }
        
        # Ensure summaries are never empty
        if not results["summary"]:
            results["summary"] = "Analyse du contenu en cours..."
        if not results["detailed_summary"]:
            results["detailed_summary"] = "Une analyse détaillée est en cours de génération..."
            
        logger.info("Successfully analyzed content using DeepSeek AI")
        print(f"Final results: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Error using DeepSeek AI: {e}")
        # Instead of fallback, raise the exception to show a clear error message
        error_message = f"Error in AI analysis: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)


# No need to load models automatically since we're using OpenRouter API

