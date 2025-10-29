"""
Main AI orchestration layer for multimodal analysis.
This module uses OpenRouter to access Mistral AI's free model (mistral-nemo) for multimodal analysis.
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

# API keys from settings
OPENROUTER_API_KEY = getattr(settings, 'OPENROUTER_API_KEY', '')
ASSEMBLYAI_API_KEY = getattr(settings, 'ASSEMBLYAI_API_KEY', '')

# No need for load_all_models function since we're using OpenRouter API


def transcribe_audio_with_whisper(audio_path):
    """
    Transcribe audio using AssemblyAI's official Python SDK (FREE $50 credits!).
    Much simpler and more reliable than the REST API.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: The transcription of the audio, or None if transcription failed
    """
    try:
        logger.info("="*80)
        logger.info("SPEECH-TO-TEXT: Starting audio transcription with AssemblyAI SDK (FREE)...")
        logger.info("="*80)
        logger.info(f"Transcribing audio file: {audio_path}")
        
        # Check if AssemblyAI API key is available
        if not ASSEMBLYAI_API_KEY:
            logger.error("ERROR: AssemblyAI API key not found in settings!")
            logger.error("Get your FREE API key at: https://www.assemblyai.com/")
            logger.error("Then add ASSEMBLYAI_API_KEY to your settings.py file")
            logger.error("="*80)
            return None
        
        # Import AssemblyAI SDK
        try:
            import assemblyai as aai
        except ImportError:
            logger.error("ERROR: AssemblyAI SDK not installed!")
            logger.error("Run: pip install assemblyai")
            logger.error("="*80)
            return None
        
        # Configure AssemblyAI with API key
        aai.settings.api_key = ASSEMBLYAI_API_KEY
        
        logger.info(f"Transcribing audio file: {os.path.basename(audio_path)}")
        logger.info("Using AssemblyAI SDK to transcribe audio")
        
        # Create transcriber and transcribe the audio file
        # The SDK handles upload and polling automatically!
        transcriber = aai.Transcriber()
        
        # Configure for French language
        config = aai.TranscriptionConfig(language_code="fr")
        
        logger.info("Uploading and processing...")
        transcript = transcriber.transcribe(audio_path, config=config)
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"Transcription failed: {transcript.error}")
            logger.error("="*80)
            return None
        
        transcription = transcript.text.strip()
        
        if transcription:
            logger.info("TRANSCRIPTION COMPLETED!")
            logger.info(f"Transcribed text: {transcription}")
            logger.info("="*80)
            return transcription
        else:
            logger.error("No transcription text in response")
            logger.error("="*80)
            return None
        
    except Exception as e:
        logger.error(f"ERROR during transcription: {e}")
        logger.error("="*80)
        return None


def analyze_multimodal_content(text=None, audio_path=None, image_path=None):
    """
    Analyze multimodal content (text, audio, image) using appropriate AI models via OpenRouter.
    - Text analysis: mistralai/mistral-nemo:free
    - Image analysis: google/gemini-2.0-flash-exp:free (supports vision)
    - Audio: Transcribed first using OpenAI Whisper API, then analyzed
    
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
    audio_base64 = None
    image_base64 = None
    audio_transcription = None
    
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
    
    # Process audio file if provided - transcribe it first using Speech-to-Text
    if audio_path:
        try:
            # First, transcribe the audio using Speech-to-Text (AssemblyAI)
            logger.info(f"Processing audio file: {os.path.basename(audio_path)}")
            print("\n" + "="*80)
            print("SPEECH-TO-TEXT (AssemblyAI): Starting transcription...")
            print("="*80)
            audio_transcription = transcribe_audio_with_whisper(audio_path)
            
            if audio_transcription:
                print("\n" + "="*80)
                print("TRANSCRIPTION RESULT:")
                print(f'"{audio_transcription}"')
                print("="*80 + "\n")
                logger.info("Speech-to-Text completed successfully!")
                logger.info(f"Transcribed text: {audio_transcription[:100]}{'...' if len(audio_transcription) > 100 else ''}")
                content_parts.append(f"AUDIO SPEECH-TO-TEXT TRANSCRIPTION (mot pour mot): {audio_transcription}")
                content_parts.append("IMPORTANT: Cette transcription provient d'un système Speech-to-Text professionnel et représente EXACTEMENT ce qui a été dit dans l'audio. Base ton analyse émotionnelle sur le CONTENU RÉEL de cette transcription, pas sur des hypothèses.")
            else:
                logger.warning("Audio transcription failed, skipping audio analysis")
                logger.warning("Speech-to-Text transcription failed - audio analysis will be skipped")
                content_parts.append("AUDIO FILE: Transcription non disponible")
                
            # Also encode audio for potential future use
            with open(audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                logger.info(f"Encoded audio file to base64: {len(audio_base64)} characters")
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            logger.error(f"Error processing audio: {e}")
            content_parts.append("AUDIO FILE: Erreur lors du traitement")
    
    # Process image file if provided
    if image_path:
        try:
            # Read and encode image file to base64
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                logger.info(f"Encoded image file to base64: {len(image_base64)} characters")
        except Exception as e:
            logger.error(f"Error encoding image file: {e}")
        
        content_parts.append(f"IMAGE FILE: {os.path.basename(image_path)}")
        content_parts.append("IMPORTANT POUR L'ANALYSE D'IMAGE: Examine attentivement les expressions faciales, la posture corporelle et l'ambiance générale. Sois particulièrement vigilant pour détecter les signes de tristesse, d'anxiété, de stress ou d'autres émotions négatives. Ne présume pas que les gens sourient ou sont heureux par défaut.")
    
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
8. Pour les images, ANALYSE ATTENTIVEMENT les expressions faciales et le langage corporel pour détecter les émotions négatives comme la tristesse, la mélancolie, l'anxiété ou la dépression.
9. Ne présume JAMAIS qu'une personne est heureuse dans une image sans preuves claires (sourire évident, posture joyeuse, etc.).
10. Si une image montre des signes de tristesse ou d'émotions négatives, reflète cela précisément dans ton analyse.
11. N'utilise PAS de caractères spéciaux ou Unicode rares - utilise uniquement des caractères ASCII standard et des caractères français courants.
12. Assure-toi que la réponse JSON est valide et ne contient pas de caractères qui pourraient causer des problèmes d'encodage.
13. Si une transcription audio est fournie dans le contenu, base ton analyse sur le CONTENU EXACT de la transcription, pas sur des hypothèses.
"""
    
    try:
        # Call OpenRouter API to analyze content
        logger.info("Sending request to OpenRouter AI...")
        
        # Prepare the request payload with a more detailed system prompt
        # Build the user message content
        user_message_content = []
        
        # Add text prompt
        user_message_content.append({
            "type": "text",
            "text": prompt
        })
        
        # Add image if provided (using data URL format)
        if image_base64:
            # Determine image type from file extension
            image_ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(image_ext, 'image/jpeg')
            
            user_message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_base64}"
                }
            })
            logger.info(f"Added image to request with MIME type: {mime_type}")
        
        # Note: Audio is transcribed separately using Whisper, so we don't send audio_url anymore
        
        # Choose the right model based on content type
        # Use Google Gemini Flash (free) for images as it supports vision
        # Use Mistral Nemo (free) for text-only analysis
        if image_base64:
            model_name = "google/gemini-2.0-flash-exp:free"
            logger.info("Using Google Gemini Flash for image analysis")
        else:
            model_name = "mistralai/mistral-nemo:free"
            logger.info("Using Mistral Nemo for text analysis")
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "Tu es un assistant d'analyse avancé spécialisé dans l'analyse de journaux personnels. Tu excelles dans l'analyse de texte, audio et images pour en extraire des insights profonds. Tu es PARTICULIÈREMENT doué pour détecter avec précision les émotions réelles dans les expressions faciales, le langage corporel et le ton vocal, qu'elles soient positives (joie, enthousiasme, sérénité) ou négatives (tristesse, anxiété, colère). Pour l'audio, tu commences TOUJOURS par transcrire EXACTEMENT ce qui est dit, mot pour mot, avant de faire ton analyse. NE FABRIQUE JAMAIS une transcription - si tu ne peux pas comprendre l'audio clairement, indique simplement 'Transcription non claire' au lieu d'inventer du contenu. Tu fournis toujours des analyses détaillées, empathiques et pertinentes en français. Tu réponds UNIQUEMENT avec du JSON valide, sans texte supplémentaire. Tes résumés sont toujours personnalisés, utilisant la forme 'tu', et offrent des perspectives significatives. IMPORTANT: N'utilise PAS de caractères spéciaux ou Unicode rares dans tes réponses - utilise uniquement des caractères ASCII standard et des caractères français courants pour éviter les problèmes d'encodage."},
                {"role": "user", "content": user_message_content if len(user_message_content) > 1 else prompt}
            ]
        }
        
        # Make the API request using the exact format provided with proper encoding
        # Ajout des paramètres requis par OpenRouter
        if "max_tokens" not in payload:
            payload["max_tokens"] = 1000
        if "temperature" not in payload:
            payload["temperature"] = 0.7
            
        # Log the payload for debugging
        logger.info(f"Sending payload to OpenRouter: {json.dumps(payload, ensure_ascii=False)}")
            
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "MindScribe Journal"
            },
            json=payload  # Using json parameter instead of data for proper JSON handling
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        ai_response = response_data["choices"][0]["message"]["content"]
        logger.info(f"Received response from OpenRouter AI")
        print(f"Raw response from OpenRouter AI: {ai_response}")
        
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
            logger.info(f"Successfully parsed JSON from OpenRouter AI")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            try:
                # First level of cleaning - handle basic encoding issues
                cleaned_response = ai_response.encode('utf-8', errors='ignore').decode('utf-8')
                ai_results = json.loads(cleaned_response)
                logger.info("Successfully parsed JSON after basic cleaning from OpenRouter AI")
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
            # Use the REAL transcription from Whisper, not the AI's fabricated one
            "audio_transcription": audio_transcription if audio_transcription else ai_results.get("audio_transcription"),
            "image_caption": ai_results.get("image_caption"),
            "image_scene": ai_results.get("image_scene"),
            "image_analysis": ai_results.get("image_analysis")
        }
        
        # If any required fields are missing, raise an error
        required_fields = ["sentiment", "emotion_score", "keywords", "summary", "topics"]
        missing_fields = [field for field in required_fields if results.get(field) is None]
        if missing_fields:
            raise Exception(f"Error in AI analysis: Missing required fields in AI response: {', '.join(missing_fields)}")
            
        logger.info("Successfully analyzed content using OpenRouter AI")
        
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
        logger.error(f"HTTP error using OpenRouter AI: {e}")
        
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
        logger.error(f"Error using OpenRouter AI: {e}")
        error_message = f"Error in AI analysis: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)


# Fonction de fallback supprimée pour utiliser uniquement l'API OpenRouter


# No need to load models automatically since we're using OpenRouter API

