# communication/services/ai_service.py
import logging
import time
import requests
import json
import random
from typing import Dict, Optional
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from journal.models import Journal
from communication.models import AssistantIA
from django.db.models import Count

logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
        self.base_url = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.default_model = getattr(settings, 'OPENROUTER_MODEL', 'google/gemini-pro')
        self.config = getattr(settings, 'AI_CONFIG', {})
        self.fallback_models = list(getattr(settings, 'OPENROUTER_MODELS', {}).values())
        self._debug_configuration()
    
    def _debug_configuration(self):
        print("=" * 50)
        print("DEBUG CONFIGURATION")
        print(f"OPENROUTER_API_KEY: '{self.api_key}'")
        print(f"OPENROUTER_API_KEY length: {len(self.api_key)}")
        print(f"OPENROUTER_BASE_URL: {self.base_url}")
        print(f"OPENROUTER_MODEL: {self.default_model}")
        print(f"OPENROUTER_MODELS: {self.fallback_models}")
        print(f"AI_CONFIG: {self.config}")
        print("=" * 50)
    
    def generer_reponse(self, prompt: str, model: str = None, **kwargs) -> Dict:
        if not self.api_key:
            logger.warning("OpenRouter API key non configurée - utilisation du mode simulation")
            return self._generer_reponse_intelligente(prompt)
        
        models_to_try = [model] if model else [self.default_model] + self.fallback_models
        
        for current_model in models_to_try:
            try:
                logger.info(f"Essai avec le modèle: {current_model}")
                result = self._call_openrouter_api(prompt, current_model, **kwargs)
                if result['success']:
                    logger.info(f"✅ Succès avec {current_model}")
                    return result
                else:
                    logger.warning(f"Échec avec {current_model}, essaye le suivant...")
            except Exception as e:
                logger.warning(f"Erreur avec {current_model}: {str(e)}, essaye le suivant...")
                continue
                
        logger.error("Tous les modèles ont échoué, utilisation du mode simulation")
        fallback_response = self._generer_reponse_intelligente(prompt)
        return {
            'success': True,
            'reponse': fallback_response.get('reponse', ''),
            'tokens_utilises': fallback_response.get('tokens_utilises', 0),
            'duree_generation': fallback_response.get('duree_generation', '0.1s'),
            'modele_utilise': fallback_response.get('modele_utilise', 'assistant_mindscribe'),
            'date_interaction': fallback_response.get('date_interaction', timezone.now().strftime('%H:%M')),
        }
    
    def _call_openrouter_api(self, prompt: str, model: str, **kwargs) -> Dict:
        print("🚀 ========== DÉBUT APPEL OPENROUTER API ==========")
        print(f"📝 PROMPT ENVOYÉ ({len(prompt)} caractères):")
        print(f"\"{prompt}\"")
        print(f"🔧 CONFIGURATION: Model={model}, Max Tokens={kwargs.get('max_tokens', self.config.get('max_tokens', 800))}")
        
        start_time = time.time()
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': getattr(settings, 'SITE_URL', 'https://mindscribe.com'),
                'X-Title': getattr(settings, 'SITE_NAME', 'MindScribe'),
            }
            
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': kwargs.get('max_tokens', self.config.get('max_tokens', 800)),
                'temperature': kwargs.get('temperature', self.config.get('temperature', 0.7)),
            }
            
            logger.info(f"Envoi requête à OpenRouter avec modèle: {model}")
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=self.config.get('timeout', 60)
            )
            
            logger.info(f"Réponse OpenRouter - Status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            
            duree = time.time() - start_time
            
            return {
                'success': True,
                'reponse': data['choices'][0]['message']['content'],
                'tokens_utilises': data.get('usage', {}).get('total_tokens', 0),
                'duree_generation': f"{duree:.2f}s",
                'modele_utilise': model,
                'date_interaction': timezone.now().strftime('%H:%M'),
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API OpenRouter avec {model}: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erreur inattendue avec {model}: {str(e)}")
            raise e
    
    def _generer_reponse_intelligente(self, prompt: str) -> Dict:
        prompt_lower = prompt.lower().strip()
        reponses = []
        
        if any(mot in prompt_lower for mot in ['bonjour', 'salut', 'hello']):
            reponses = [
                "👋 Bonjour ! Je suis MindScribe, votre compagnon d'écriture. Prêt à explorer vos pensées ?",
                "😊 Salut ! Content de vous revoir. De quoi avez-vous envie de parler ?",
            ]
        elif any(phrase in prompt_lower for phrase in ['how are you', 'comment vas-tu']):
            reponses = [
                "😊 Je vais bien, merci ! Et vous, comment allez-vous ?",
                "🌟 Toujours prêt à aider ! Et vous, ça va ?",
            ]
        elif any(phrase in prompt_lower for phrase in ['créer un journal', 'nouveau journal']):
            reponses = [
                "📖 Super ! Allez dans 'Mes Journaux' et cliquez sur 'Nouveau Journal'. Besoin d'inspiration ?",
                "🎉 Votre espace d'écriture vous attend. Direction 'Mes Journaux' → 'Nouveau'.",
            ]
        elif any(mot in prompt_lower for mot in ['écrire', 'noter', 'rédiger']):
            reponses = [
                "✍️ Envie d'écrire ? Qu'est-ce qui vous inspire aujourd'hui ?",
                "📚 L'écriture libère l'esprit. Par où commencer ?",
            ]
        elif any(mot in prompt_lower for mot in ['suggestion', 'idée']):
            reponses = [
                "💡 Idées : un souvenir, vos objectifs, ou une émotion du moment.",
                "🎯 Essayez d'écrire sur votre journée idéale ou une réflexion personnelle.",
            ]
        elif any(mot in prompt_lower for mot in ['analyse', 'analyser']):
            reponses = [
                "🔍 Sélectionnez un journal à gauche pour une analyse détaillée.",
                "📊 Choisissez un journal pour explorer ses thèmes et émotions.",
            ]
        elif any(mot in prompt_lower for mot in ['triste', 'heureux', 'stress']):
            reponses = [
                "💖 Je sens une émotion forte. L'écriture peut aider. Parlez-m'en ?",
                "🤗 Vos émotions sont importantes. Souhaitez-vous les exprimer ?",
            ]
        else:
            reponses = [
                f"🤔 '{prompt}'... Intéressant ! Pouvez-vous développer ?",
                f"💭 '{prompt}'... Racontez-m'en plus !",
            ]
        
        reponse_text = random.choice(reponses)
        return {
            'success': True,
            'reponse': reponse_text,
            'tokens_utilises': len(reponse_text.split()),
            'duree_generation': '0.1s',
            'modele_utilise': 'assistant_mindscribe',
            'date_interaction': timezone.now().strftime('%H:%M'),
        }

class AIServiceManager:
    def __init__(self):
        self.openrouter = OpenRouterService()
    
    def traiter_interaction(self, utilisateur, message: str, journal=None, session_id=None, contexte: Dict = None) -> Dict:
        if not message or len(message.strip()) == 0:
            return {'success': False, 'error': 'Message vide'}
        
        if len(message) > 2000:
            return {'success': False, 'error': 'Message trop long'}
        
        message = message.strip()[:2000]
        start_time = time.time()
        contexte = contexte or {}
        
        try:
            type_interaction = self._detecter_type_interaction(message, journal)
            prompt = self._construire_prompt_complet(utilisateur, message, journal, session_id, type_interaction, contexte)
            resultat = self.openrouter.generer_reponse(prompt)
            
            # Handle both direct response and fallback response
            reponse_complete = resultat.get('reponse', '')
            if not reponse_complete and 'reponse_fallback' in resultat:
                reponse_complete = resultat.get('reponse_fallback', '')
            
            if isinstance(reponse_complete, dict):
                reponse_complete = reponse_complete.get('reponse', '')
            
            reponse_clean = self._nettoyer_reponse(reponse_complete)
            score_confiance = self._calculer_score_confiance(resultat)
            mots_cles = self._extraire_mots_cles(message)
            sentiment = self._detecter_sentiment(message)
            
            conversation = AssistantIA.objects.create(
                utilisateur=utilisateur,
                journal=journal,
                session_id=session_id,
                message_utilisateur=message,
                reponse_ia=reponse_clean,
                type_interaction=type_interaction,
                statut='termine' if resultat.get('success', True) else 'erreur',
                modele_utilise=resultat.get('modele_utilise', 'simulation'),
                prompt_utilise=prompt,
                tokens_utilises=resultat.get('tokens_utilises', 0),
                duree_generation=float(resultat.get('duree_generation', '0').replace('s', '')),
                score_confiance=score_confiance,
                mots_cles=mots_cles,
                sentiment_utilisateur=sentiment,
            )
            
            return {
                'success': True,
                'conversation_id': str(conversation.id),
                'reponse': conversation.reponse_ia,
                'type_interaction': conversation.type_interaction,
                'type_interaction_display': conversation.get_type_interaction_display(),
                'date_interaction': conversation.date_creation.strftime('%H:%M'),
                'statistiques': {
                    'tokens_utilises': conversation.tokens_utilises,
                    'duree_generation': conversation.duree_formatee,
                    'score_confiance': conversation.score_confiance
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement interaction: {str(e)}")
            # Return a fallback response instead of error
            fallback_response = self._generer_reponse_intelligente(message)
            return {
                'success': True,
                'reponse': fallback_response.get('reponse', 'Je rencontre une difficulté technique. Pouvez-vous reformuler votre question ?'),
                'date_interaction': timezone.now().strftime('%H:%M'),
                'type_interaction': 'question',
                'statistiques': {
                    'tokens_utilises': 0,
                    'duree_generation': '0.1s',
                    'score_confiance': 0.3
                }
            }
    
    def _detecter_type_interaction(self, message: str, journal=None) -> str:
        message_lower = message.lower()
        mots_analyse = ['analyse', 'analyser', 'commente', 'pense', 'que dire']
        mots_suggestion = ['suggère', 'suggestion', 'idée', 'exercice', 'écrire']
        mots_support = ['triste', 'heureux', 'stress', 'anxieux', 'émotion', 'sentiment']
        mots_reflexion = ['réfléchir', 'penser', 'philosophie', 'question existentielle']
        
        if any(mot in message_lower for mot in mots_analyse) and journal:
            return 'analyse_journal'
        elif any(mot in message_lower for mot in mots_suggestion):
            return 'suggestion_ecriture'
        elif any(mot in message_lower for mot in mots_support):
            return 'support_emotionnel'
        elif any(mot in message_lower for mot in mots_reflexion):
            return 'reflexion_guidee'
        else:
            return 'question'
    
    def _construire_prompt_complet(self, utilisateur, message: str, journal=None, session_id=None, type_interaction: str = None, contexte: Dict = None) -> str:
        prenom = utilisateur.first_name or utilisateur.username
        contexte_journal = ""
        if journal:
            contenu = journal.contenu_texte
            if journal.type_entree == 'audio' and journal.audio:
                contenu = f"[Audio: {journal.audio.name}]"
            elif journal.type_entree == 'image' and journal.image:
                contenu = f"[Image: {journal.image.name}]"
            contenu_limite = contenu[:800] + "..." if len(contenu) > 800 else contenu
            contexte_journal = f"""
JOURNAL À ANALYSER:
- Date: {journal.date_creation.strftime('%d/%m/%Y')}
- Type: {journal.type_entree}
- Catégorie: {journal.categorie or 'Non catégorisé'}
- Contenu: {contenu_limite}
"""
        
        historique = ""
        if session_id:
            conversations_recentes = AssistantIA.objects.filter(
                session_id=session_id
            ).order_by('-date_creation')[:3]
            if conversations_recentes:
                historique_lines = []
                for conv in reversed(conversations_recentes):
                    msg = conv.message_utilisateur[:200] + "..." if len(conv.message_utilisateur) > 200 else conv.message_utilisateur
                    reponse = conv.reponse_ia[:200] + "..." if len(conv.reponse_ia) > 200 else conv.reponse_ia
                    historique_lines.append(f"UTILISATEUR: {msg}")
                    historique_lines.append(f"ASSISTANT: {reponse}")
                historique = "\nHISTORIQUE RÉCENT:\n" + "\n".join(historique_lines)
        
        instructions_specifiques = self._get_instructions_par_type(type_interaction)
        
        prompt = f"""
# CONTEXTE
Tu parles à {prenom}, l'utilisateur qui a écrit le journal.
Type d'interaction: {type_interaction}

{contexte_journal}
{historique}

# INSTRUCTIONS GÉNÉRALES
Tu es MindScribe, assistant expert en écriture de journal et développement personnel.
IMPORTANT: Tu réponds toujours à {prenom} (l'utilisateur), PAS à toi-même. 
Quand tu analyses un journal, c'est le JOURNAL DE {prenom.upper()}, pas le tien.

{instructions_specifiques}

## TON STYLE
- Chaleureux et empathique envers {prenom}
- Encourageant et positif
- Professionnel mais accessible
- Adapte ton ton au type d'interaction
- Réponds toujours en français
- Utilise "vous" ou {prenom} pour t'adresser à l'utilisateur
- N'utilise jamais "je suis ravi" ou des phrases qui parlent de toi - parle directement à {prenom}

## MESSAGE UTILISATEUR
"{message}"

## TA RÉPONSE:
"""
        return prompt.strip()
    
    def _get_instructions_par_type(self, type_interaction: str) -> str:
        instructions = {
            'analyse_journal': """
## POUR L'ANALYSE DE JOURNAL
- Tu analyses le journal de l'utilisateur, PAS le tien
- Identifie les thèmes principaux dans leur journal
- Souligne les émotions exprimées par l'utilisateur
- Propose des insights constructifs sur LEUR contenu
- Encourage la réflexion personnelle de l'utilisateur
- Parle directement à l'utilisateur comme "Vous avez exprimé..." ou "Votre journal montre..."
- Si le journal est audio/image, commente sur le contexte ou le type de média
- N'utilise jamais "Bonjour Test" ou le nom par défaut - utilise le vrai prénom de l'utilisateur
            """,
            'suggestion_ecriture': """
## POUR LES SUGGESTIONS D'ÉCRITURE
- Propose des idées créatives et personnalisées
- Donne des exercices d'écriture concrets
- Inspire la réflexion et l'introspection
            """,
            'support_emotionnel': """
## POUR LE SUPPORT ÉMOTIONNEL
- Fais preuve d'empathie et de compassion
- Valide les émotions exprimées
- Propose des perspectives positives
            """,
            'reflexion_guidee': """
## POUR LA RÉFLEXION GUIDÉE
- Pose des questions stimulantes
- Guide vers des insights personnels
- Encourage l'auto-réflexion
            """,
            'question': """
## POUR LES QUESTIONS GÉNÉRALES
- Réponds de manière claire et utile
- Propose des ressources supplémentaires si besoin
            """
        }
        return instructions.get(type_interaction, instructions['question'])
    
    def _nettoyer_reponse(self, reponse: str) -> str:
        if not reponse:
            return "Je n'ai pas pu générer de réponse. Pouvez-vous reformuler ?"
        return ' '.join(reponse.split()).strip()
    
    def _extraire_mots_cles(self, message: str) -> list:
        try:
            stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'mais', 'donc'}
            mots = message.lower().split()
            mots_filtres = [mot for mot in mots if len(mot) > 3 and mot not in stop_words]
            return list(set(mots_filtres))[:10]
        except:
            return []
    
    def _detecter_sentiment(self, message: str) -> str:
        message_lower = message.lower()
        mots_positifs = {'heureux', 'content', 'joyeux', 'génial', 'super'}
        mots_negatifs = {'triste', 'malheureux', 'déprimé', 'stress', 'anxieux'}
        
        if any(mot in message_lower for mot in mots_positifs):
            return 'positif'
        elif any(mot in message_lower for mot in mots_negatifs):
            return 'negatif'
        return 'neutre'
    
    def _calculer_score_confiance(self, resultat: Dict) -> float:
        score = 0.5
        if not isinstance(resultat, dict):
            return 0.3
        if resultat.get('success', False):
            score += 0.3
            if resultat.get('tokens_utilises', 0) > 50:
                score += 0.1
            if float(resultat.get('duree_generation', '0').replace('s', '')) < 10:
                score += 0.1
        return min(score, 1.0)
    
    def get_statistiques_utilisateur(self, utilisateur):
        try:
            conversations = AssistantIA.objects.filter(utilisateur=utilisateur)
            if not conversations.exists():
                return {
                    'total_conversations': 0,
                    'total_tokens': 0,
                    'types_interactions': {},
                    'derniere_interaction': None,
                    'modele_prefere': None
                }
            
            total_conversations = conversations.count()
            total_tokens = sum(conv.tokens_utilises for conv in conversations)
            types_data = conversations.values('type_interaction').annotate(count=Count('id'))
            types_interactions = {item['type_interaction']: item['count'] for item in types_data}
            derniere_interaction = conversations.order_by('-date_creation').first()
            modele_data = conversations.values('modele_utilise').annotate(count=Count('id')).order_by('-count').first()
            modele_prefere = modele_data['modele_utilise'] if modele_data else None
            
            return {
                'total_conversations': total_conversations,
                'total_tokens': total_tokens,
                'types_interactions': types_interactions,
                'derniere_interaction': derniere_interaction,
                'modele_prefere': modele_prefere
            }
        except Exception as e:
            logger.error(f"Erreur calcul statistiques: {str(e)}")
            return {
                'total_conversations': 0,
                'total_tokens': 0,
                'types_interactions': {},
                'derniere_interaction': None,
                'modele_prefere': None
            }

ai_service = AIServiceManager()