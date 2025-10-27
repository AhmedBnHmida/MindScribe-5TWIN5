"""
Main AI orchestration layer for multimodal analysis.
This module uses OpenRouter to access Mistral AI for multimodal analysis.
"""
import os
import logging
import json
import requests
import base64
import re
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# OpenRouter API key
OPENROUTER_API_KEY = "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"

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
    
    # Add text content if provided with proper encoding handling
    if text:
        # Ensure text is properly encoded to handle special characters
        try:
            # Try to normalize the text encoding
            normalized_text = text.encode('utf-8', errors='ignore').decode('utf-8')
            content_parts.append(f"TEXT CONTENT: {normalized_text}")
        except Exception as e:
            logger.warning(f"Error normalizing text: {e}")
            # Fall back to the original text
            content_parts.append(f"TEXT CONTENT: {text}")
    
    # Process audio file if provided
    if audio_path:
        content_parts.append(f"AUDIO FILE: {os.path.basename(audio_path)}")
    
    # Process image file if provided
    if image_path:
        content_parts.append(f"IMAGE FILE: {os.path.basename(image_path)}")
    
    # Combine all content
    combined_content = "\n\n".join(content_parts)
    
    # If no content provided, return an error
    if not combined_content:
        raise Exception("Aucun contenu à analyser. Veuillez fournir du texte, un fichier audio ou une image.")
    
    # Create an enhanced prompt with more detailed analysis requirements
    prompt = f"""Analyze the following content and provide a VERY detailed structured analysis in French:

{combined_content}

Please provide the following information in a structured JSON format:
{{
  "sentiment": "positif/neutre/negatif",
  "emotion_score": 0.0-1.0,
  "emotions_detected": ["emotion1", "emotion2", "emotion3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "summary": "Un résumé clair et concis qui capture l'essence du contenu en utilisant la forme 'tu'",
  "detailed_summary": "Un résumé détaillé avec une analyse approfondie du contenu, incluant les thèmes principaux, les émotions et les réflexions importantes. Ce résumé doit être personnalisé, utiliser la forme 'tu' et offrir des perspectives significatives sur le contenu.",
  "topics": ["topic1", "topic2", "topic3"],
  "positive_aspects": ["aspect positif 1", "aspect positif 2", "aspect positif 3"],
  "negative_aspects": ["aspect négatif 1", "aspect négatif 2", "aspect négatif 3"],
  "action_items": ["action suggérée 1", "action suggérée 2", "action suggérée 3"],
  "mood_analysis": "Une analyse approfondie de l'humeur et de l'état émotionnel, avec des observations sur les nuances et les variations d'émotions",
  "audio_transcription": "transcription si un fichier audio est fourni",
  "image_caption": "description si une image est fournie",
  "image_scene": "type de scène si une image est fournie",
  "image_analysis": "analyse approfondie de ce que l'image représente dans son contexte"
}}

INSTRUCTIONS CRITIQUES:
1. Réponds UNIQUEMENT avec l'objet JSON, sans texte supplémentaire.
2. Le résumé doit être clair, concis et personnalisé (utilise la forme 'tu').
3. Le résumé détaillé doit être TRÈS approfondi, avec au moins 4-5 phrases complètes.
4. Identifie des aspects positifs et négatifs spécifiques tirés du contenu.
5. Suggère des actions concrètes et pertinentes basées sur le contenu.
6. Toute l'analyse doit être en français et rédigée avec un ton bienveillant et empathique.
7. L'analyse d'humeur doit être détaillée et nuancée, pas seulement superficielle.
8. N'utilise PAS de caractères spéciaux ou Unicode rares - utilise uniquement des caractères ASCII standard et des caractères français courants.
9. Assure-toi que la réponse JSON est valide et ne contient pas de caractères qui pourraient causer des problèmes d'encodage.
"""
    
    try:
        # Call DeepSeek model via OpenRouter direct API - WAIT for the response
        logger.info("Sending request to DeepSeek AI...")
        
        # Prepare the request payload with a more detailed system prompt
        payload = {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": [
                {"role": "system", "content": "Tu es un assistant d'analyse avancé spécialisé dans l'analyse de journaux personnels. Tu excelles dans l'analyse de texte, audio et images pour en extraire des insights profonds. Tu fournis toujours des analyses détaillées, empathiques et pertinentes en français. Tu réponds UNIQUEMENT avec du JSON valide, sans texte supplémentaire. Tes résumés sont toujours personnalisés, utilisant la forme 'tu', et offrent des perspectives significatives. IMPORTANT: N'utilise PAS de caractères spéciaux ou Unicode rares dans tes réponses - utilise uniquement des caractères ASCII standard et des caractères français courants pour éviter les problèmes d'encodage."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Make the API request using the exact format provided with proper encoding
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json; charset=utf-8",
                "HTTP-Referer": "https://mindscribe-journal.com",
                "X-Title": "MindScribe Journal"
            },
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
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
            
        # Parse JSON response with thorough encoding handling
        try:
            # First attempt to parse the JSON as is
            ai_results = json.loads(ai_response)
            logger.info(f"Successfully parsed JSON from DeepSeek AI")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            try:
                # First level of cleaning - handle basic encoding issues
                cleaned_response = ai_response.encode('utf-8', errors='ignore').decode('utf-8')
                ai_results = json.loads(cleaned_response)
                logger.info("Successfully parsed JSON after basic cleaning")
            except json.JSONDecodeError:
                try:
                    # Second level of cleaning - remove problematic characters
                    cleaned_response = ''.join(c for c in cleaned_response if ord(c) < 65536 and c.isprintable())
                    ai_results = json.loads(cleaned_response)
                    logger.info("Successfully parsed JSON after removing problematic characters")
                except json.JSONDecodeError:
                    try:
                        # Third level of cleaning - try to fix common JSON syntax errors
                        cleaned_response = cleaned_response.replace("'", '"')  # Replace single quotes with double quotes
                        cleaned_response = re.sub(r',\s*}', '}', cleaned_response)  # Remove trailing commas
                        cleaned_response = re.sub(r',\s*]', ']', cleaned_response)  # Remove trailing commas in arrays
                        ai_results = json.loads(cleaned_response)
                        logger.info("Successfully parsed JSON after fixing syntax errors")
                    except Exception as parse_error:
                        logger.error(f"Failed to parse JSON after multiple cleaning attempts: {parse_error}")
                        # If all parsing attempts fail, raise a clear error
                        raise Exception(f"Error in AI analysis: Unable to parse AI response as JSON after multiple attempts")
        
        # Use the AI results directly without any fallback values
        results = {
            "sentiment": ai_results.get("sentiment"),
            "emotion_score": ai_results.get("emotion_score"),
            "emotions_detected": ai_results.get("emotions_detected"),
            "keywords": ai_results.get("keywords"),
            "summary": ai_results.get("summary"),
            "detailed_summary": ai_results.get("detailed_summary"),
            "topics": ai_results.get("topics"),
            "positive_aspects": ai_results.get("positive_aspects"),
            "negative_aspects": ai_results.get("negative_aspects"),
            "action_items": ai_results.get("action_items"),
            "mood_analysis": ai_results.get("mood_analysis"),
            "audio_transcription": ai_results.get("audio_transcription"),
            "image_caption": ai_results.get("image_caption"),
            "image_scene": ai_results.get("image_scene"),
            "image_analysis": ai_results.get("image_analysis")
        }
        
        # If any required fields are missing, raise an error
        required_fields = ["sentiment", "emotion_score", "keywords", "summary", "topics"]
        missing_fields = [field for field in required_fields if results.get(field) is None]
        if missing_fields:
            raise Exception(f"Error in AI analysis: Missing required fields in AI response: {', '.join(missing_fields)}")
            
        logger.info("Successfully analyzed content using DeepSeek AI")
        
        # Define a recursive function to sanitize all strings in the results
        def sanitize_value(value):
            if isinstance(value, str):
                # First, normalize the string to remove problematic characters
                sanitized = value.encode('utf-8', errors='ignore').decode('utf-8')
                # Then, remove any characters that can't be encoded in charmap
                sanitized = ''.join(c for c in sanitized if ord(c) < 65536 and c.isprintable())
                return sanitized
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            else:
                return value
        
        # Apply the sanitization function to all values in the results
        results = sanitize_value(results)
        
        print(f"Final results: {results}")
        return results
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error using DeepSeek AI: {e}")
        
        # Log specific error details based on status code
        if e.response.status_code == 401:
            error_message = "Error in AI analysis: API key is invalid or expired. Please check your OpenRouter API key."
        elif e.response.status_code == 403:
            error_message = "Error in AI analysis: API access forbidden. Please check your permissions."
        elif e.response.status_code == 429:
            error_message = "Error in AI analysis: Rate limit exceeded. Please try again later."
        else:
            error_message = f"Error in AI analysis: HTTP error {e.response.status_code} - {str(e)}"
        
        logger.error(error_message)
        raise Exception(error_message)
    
    except Exception as e:
        logger.error(f"Error using DeepSeek AI: {e}")
        error_message = f"Error in AI analysis: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)


# No need to load models automatically since we're using OpenRouter API

