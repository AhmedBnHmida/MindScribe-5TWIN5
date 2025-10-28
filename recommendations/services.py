"""
AI-powered recommendation service using OpenRouter API.
Generates personalized recommendations based on journal analysis.
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.conf import settings
from module2_analysis.models import JournalAnalysis

logger = logging.getLogger(__name__)

# OpenRouter API Configuration (from settings)
OPENROUTER_API_KEY = getattr(settings, 'OPENROUTER_API_KEY', '')
OPENROUTER_API_URL = f"{getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')}/chat/completions"
OPENROUTER_MODEL = getattr(settings, 'OPENROUTER_MODEL', 'google/gemini-pro')


def get_user_analysis_summary(user, days=7):
    """
    Get a summary of user's journal analyses for the last N days.
    
    Args:
        user: User object
        days: Number of days to analyze (default 7)
        
    Returns:
        dict: Summary of user's emotional and behavioral patterns
    """
    start_date = timezone.now() - timedelta(days=days)
    
    analyses = JournalAnalysis.objects.filter(
        user=user,
        created_at__gte=start_date
    ).order_by('-created_at')
    
    if not analyses.exists():
        return {
            'total_entries': 0,
            'sentiment_distribution': {},
            'common_emotions': [],
            'common_keywords': [],
            'common_topics': [],
            'average_emotion_score': 0,
            'trend': 'insufficient_data'
        }
    
    # Calculate sentiment distribution
    sentiment_counts = {}
    all_emotions = []
    all_keywords = []
    all_topics = []
    emotion_scores = []
    
    for analysis in analyses:
        # Count sentiments
        sentiment = analysis.sentiment or 'neutre'
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Collect emotions
        if analysis.emotions_detected:
            all_emotions.extend(analysis.emotions_detected)
        
        # Collect keywords
        if analysis.keywords:
            all_keywords.extend(analysis.keywords)
        
        # Collect topics
        if analysis.topics:
            all_topics.extend(analysis.topics)
        
        # Collect emotion scores
        emotion_scores.append(analysis.emotion_score)
    
    # Find most common items
    def get_most_common(items, top_n=5):
        from collections import Counter
        if not items:
            return []
        return [item for item, count in Counter(items).most_common(top_n)]
    
    # Determine trend based on recent sentiment
    recent_analyses = list(analyses[:3])
    if len(recent_analyses) >= 2:
        recent_sentiments = [a.sentiment for a in recent_analyses]
        if all(s == 'positif' for s in recent_sentiments):
            trend = 'improving'
        elif all(s == 'negatif' for s in recent_sentiments):
            trend = 'declining'
        else:
            trend = 'stable'
    else:
        trend = 'stable'
    
    return {
        'total_entries': analyses.count(),
        'sentiment_distribution': sentiment_counts,
        'common_emotions': get_most_common(all_emotions),
        'common_keywords': get_most_common(all_keywords),
        'common_topics': get_most_common(all_topics),
        'average_emotion_score': sum(emotion_scores) / len(emotion_scores) if emotion_scores else 0,
        'trend': trend,
        'days_analyzed': days
    }


def generate_recommendations_with_ai(user, summary):
    """
    Generate personalized recommendations using OpenRouter AI.
    
    Args:
        user: User object
        summary: User analysis summary from get_user_analysis_summary()
        
    Returns:
        list: List of recommendation dictionaries
    """
    # Get the 3 most recent journal analyses
    from module2_analysis.models import JournalAnalysis
    recent_analyses = JournalAnalysis.objects.filter(
        user=user
    ).order_by('-created_at')[:3]
    
    # Extract detailed content from recent analyses
    recent_entries = []
    for analysis in recent_analyses:
        entry_data = {
            'date': analysis.created_at.strftime('%Y-%m-%d'),
            'sentiment': analysis.sentiment,
            'emotion_score': analysis.emotion_score,
            'emotions': analysis.emotions_detected,
            'keywords': analysis.keywords,
            'topics': analysis.topics,
            'summary': analysis.summary
        }
        recent_entries.append(entry_data)
    
    # Prepare the prompt for AI with more detailed journal information
    prompt = f"""Tu es un assistant de bien-être personnel spécialisé. Analyse les données suivantes d'un utilisateur de journal personnel et génère 5 recommandations TRÈS personnalisées basées sur le contenu spécifique de ses journaux.

DONNÉES DE L'UTILISATEUR (derniers {summary['days_analyzed']} jours):
- Nombre d'entrées: {summary['total_entries']}
- Distribution des sentiments: {summary['sentiment_distribution']}
- Émotions courantes: {', '.join(summary['common_emotions']) if summary['common_emotions'] else 'Aucune'}
- Mots-clés fréquents: {', '.join(summary['common_keywords']) if summary['common_keywords'] else 'Aucun'}
- Thèmes principaux: {', '.join(summary['common_topics']) if summary['common_topics'] else 'Aucun'}
- Score émotionnel moyen: {summary['average_emotion_score']:.2f}
- Tendance: {summary['trend']}

ENTRÉES DE JOURNAL RÉCENTES (détaillées):
"""

    # Add detailed journal entries to the prompt
    for i, entry in enumerate(recent_entries):
        prompt += f"""
ENTRÉE {i+1} ({entry['date']}):
- Sentiment: {entry['sentiment']}
- Score émotionnel: {entry['emotion_score']}
- Émotions: {', '.join(entry['emotions']) if entry['emotions'] else 'Non spécifié'}
- Mots-clés: {', '.join(entry['keywords']) if entry['keywords'] else 'Non spécifié'}
- Thèmes: {', '.join(entry['topics']) if entry['topics'] else 'Non spécifié'}
- Résumé: {entry['summary']}
"""

    prompt += """
INSTRUCTIONS:
Génère entre 1 et 4 recommandations TRÈS PERSONNALISÉES en fonction du contenu du journal de l'utilisateur.
Les types possibles sont:
1. Bien-être
2. Productivité
3. Sommeil
4. Nutrition

IMPORTANT:
- Choisis UNIQUEMENT les types de recommandations qui sont vraiment pertinents selon l'analyse du journal
- Ne génère PAS de recommandation pour un type si le journal ne contient pas d'information liée à ce domaine
- Génère au maximum UNE recommandation par type (pas plus)
- Chaque recommandation doit être courte (1-2 phrases max)
- Utilise un ton chaleureux et encourageant
- Sois TRÈS spécifique et actionnable, en te référant explicitement au contenu des journaux
- Adapte-toi aux émotions et tendances détectées
- Fais référence aux thèmes et préoccupations spécifiques mentionnés dans les entrées récentes
- Réponds UNIQUEMENT en JSON format strict (sans texte avant ou après):

{{
  "recommendations": [
    {{
      "type": "bien_etre|productivite|sommeil|nutrition",
      "content": "Ta recommandation ici",
      "priority": "high|medium|low"
    }}
    // Ajoute d'autres recommandations si pertinent, maximum une par type
  ]
}}"""

    try:
        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mindscribe.app",
            "X-Title": "MindScribe Recommendations"
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un assistant de bien-être expert en psychologie positive. Tu réponds UNIQUEMENT en JSON valide."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        logger.info(f"🤖 Calling OpenRouter API with model: {OPENROUTER_MODEL}")
        logger.info(f"📊 User summary - Entries: {summary['total_entries']}, Emotions: {summary['common_emotions']}")
        
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Vérifier si la réponse contient les données attendues
        if 'choices' not in result or len(result['choices']) == 0:
            logger.error(f"❌ Invalid API response format: {result}")
            return []
            
        if 'message' not in result['choices'][0] or 'content' not in result['choices'][0]['message']:
            logger.error(f"❌ Invalid message format in API response: {result['choices'][0]}")
            return []
        
        ai_response = result['choices'][0]['message']['content'].strip()
        
        if not ai_response:
            logger.error("❌ Empty response from API")
            return []
        
        logger.info(f"✅ AI Response received: {ai_response[:200]}...")
        
        # Parse JSON response
        # Remove markdown code blocks if present
        if '```json' in ai_response:
            ai_response = ai_response.split('```json')[1].split('```')[0].strip()
        elif '```' in ai_response:
            ai_response = ai_response.split('```')[1].split('```')[0].strip()
            
        # Pas de recommandations par défaut - utilisation uniquement de l'IA
        
        try:
            recommendations_data = json.loads(ai_response)
            recommendations = recommendations_data.get('recommendations', [])
            
            # Vérifier si les recommandations sont valides
            if not recommendations or not isinstance(recommendations, list):
                logger.warning("⚠️ No valid recommendations in API response")
                return []
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse JSON response")
            return []
        
        logger.info(f"🎯 Successfully generated {len(recommendations)} AI-powered recommendations!")
        return recommendations
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OpenRouter API error: {e}")
        # Retourner une liste vide en cas d'erreur
        logger.warning("⚠️ Returning empty recommendations due to API error")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing error: {e}")
        # Retourner une liste vide en cas d'erreur
        logger.warning("⚠️ Returning empty recommendations due to JSON parsing error")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error generating recommendations: {e}")
        # Retourner une liste vide en cas d'erreur
        logger.warning("⚠️ Returning empty recommendations due to unexpected error")
        return []


# La fonction de fallback a été supprimée conformément à la demande de n'utiliser que l'API OpenRouter


def create_recommendations_for_user(user):
    """
    Main function to create and save recommendations for a user.
    
    Args:
        user: User object
        
    Returns:
        list: List of created Recommendation objects
    """
    from .models import Recommandation
    
    # Get user's recent analysis summary
    summary = get_user_analysis_summary(user, days=7)
    
    if summary['total_entries'] == 0:
        logger.info(f"No journal entries for user {user.username}, skipping recommendations")
        return []
    
    # Generate AI recommendations
    recommendations_data = generate_recommendations_with_ai(user, summary)
    
    # Create recommendation objects
    created_recommendations = []
    for rec_data in recommendations_data:
        try:
            recommendation = Recommandation.objects.create(
                utilisateur=user,
                type=rec_data['type'],
                contenu=rec_data['content'],
                statut='nouvelle'
            )
            created_recommendations.append(recommendation)
            logger.info(f"Created recommendation {recommendation.id} for user {user.username}")
        except Exception as e:
            logger.error(f"Error creating recommendation: {e}")
    
    return created_recommendations


def get_user_recommendations(user, status=None, limit=10):
    """
    Get recommendations for a user.
    
    Args:
        user: User object
        status: Filter by status (optional)
        limit: Maximum number of recommendations to return
        
    Returns:
        QuerySet: Recommendations queryset
    """
    from .models import Recommandation
    
    queryset = Recommandation.objects.filter(utilisateur=user)
    
    if status:
        queryset = queryset.filter(statut=status)
    
    return queryset.order_by('-date_emission')[:limit]


def mark_recommendation_status(recommendation_id, status):
    """
    Update the status of a recommendation.
    
    Args:
        recommendation_id: UUID of the recommendation
        status: New status ('suivie' or 'ignoree')
        
    Returns:
        Recommandation: Updated recommendation object
    """
    from .models import Recommandation
    
    try:
        recommendation = Recommandation.objects.get(id=recommendation_id)
        recommendation.statut = status
        recommendation.save()
        logger.info(f"Updated recommendation {recommendation_id} status to {status}")
        return recommendation
    except Recommandation.DoesNotExist:
        logger.error(f"Recommendation {recommendation_id} not found")
        return None

