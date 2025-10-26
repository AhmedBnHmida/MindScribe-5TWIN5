import logging
import time
import requests
import json
import random
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from journal.models import Journal
from communication.models import AssistantIA
from django.db.models import Count

logger = logging.getLogger(__name__)

class OpenRouterService:
    """Service robuste avec fallback automatique"""
    
    def __init__(self):
        # Charger les paramètres quand nécessaire
        self.api_key = None
        self.base_url = None
        self.default_model = None
        self.config = None
        self.fallback_models = None
    
    def _load_settings(self):
        """Charge les paramètres quand nécessaire"""
        if self.api_key is None:
            self.api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
            self.base_url = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
            self.default_model = getattr(settings, 'OPENROUTER_MODEL', 'meta-llama/llama-3.1-8b-instruct:free')
            self.config = getattr(settings, 'AI_CONFIG', {})
            self.fallback_models = list(getattr(settings, 'OPENROUTER_MODELS', {}).values())
    
    def generer_reponse(self, prompt: str, model: str = None, **kwargs) -> Dict:
        """Génère une réponse avec fallback automatique si un modèle échoue"""
        
        self._load_settings()
        
        if not self.api_key:
            logger.warning("OpenRouter API key non configurée - utilisation du mode simulation")
            return self._generer_reponse_intelligente(prompt)
        
        models_to_try = [model] if model else [self.default_model] + self.fallback_models
        
        for current_model in models_to_try:
            try:
                logger.info(f"Essai avec le modèle: {current_model}")
                result = self._call_single_model(prompt, current_model, **kwargs)
                if result['success']:
                    logger.info(f"✅ Succès avec {current_model}")
                    return result
                else:
                    logger.warning(f"Échec avec {current_model}, essaye le suivant...")
            except Exception as e:
                logger.warning(f"Erreur avec {current_model}: {str(e)}, essaye le suivant...")
                continue
                
        logger.error("Tous les modèles ont échoué, utilisation du mode simulation")
        return {
            'success': False,
            'erreur': 'Tous les modèles ont échoué',
            'reponse_fallback': self._generer_reponse_intelligente(prompt)
        }
    
    def _call_single_model(self, prompt: str, model: str, **kwargs) -> Dict:
        """Appelle un modèle spécifique"""
        
        self._load_settings()
        
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://mindscribe.com',
                'X-Title': 'MindScribe AI Assistant'
            }
            
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': kwargs.get('max_tokens', self.config.get('max_tokens', 800)),
                'temperature': kwargs.get('temperature', self.config.get('temperature', 0.7)),
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=self.config.get('timeout', 60)
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")
                
            response.raise_for_status()
            data = response.json()
            
            duree = time.time() - start_time
            
            return {
                'success': True,
                'reponse': data['choices'][0]['message']['content'],
                'tokens_utilises': data.get('usage', {}).get('total_tokens', 0),
                'duree_generation': duree,
                'modele_utilise': model,
                'donnees_brutes': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API avec {model}: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erreur inattendue avec {model}: {str(e)}")
            raise e
    
    def _generer_reponse_intelligente(self, prompt: str) -> Dict:
        """Génère une réponse intelligente de fallback"""
        prompt_lower = prompt.lower().strip()
        
        # Détection des intentions utilisateur
        if any(mot in prompt_lower for mot in ['bonjour', 'salut', 'hello', 'coucou', 'hi', 'hey']):
            reponses = [
                "👋 Bonjour ! Je suis MindScribe, votre compagnon d'écriture. Prêt à explorer vos pensées aujourd'hui ?",
                "😊 Salut ! Content de vous revoir. De quoi avez-vous envie de parler ou d'écrire ?",
                "🌟 Hello ! Belle journée pour écrire, non ? Qu'est-ce qui vous passe par la tête en ce moment ?",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(phrase in prompt_lower for phrase in ['créer un journal', 'nouveau journal', 'commencer journal']):
            reponses = [
                "📖 Super idée ! Pour créer un journal, allez dans 'Mes Journaux' et cliquez sur 'Nouveau Journal'. Besoin d'inspiration pour commencer ?",
                "🎉 Excellent ! Votre espace d'écriture vous attend. Direction 'Mes Journaux' → 'Nouveau'. Sur quel thème aimeriez-vous écrire ?",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(mot in prompt_lower for mot in ['écrire', 'noter', 'rédiger']) and any(mot in prompt_lower for mot in ['journal', 'texte']):
            reponses = [
                "✍️ Envie d'écrire ? Excellent ! L'écriture libère l'esprit. Qu'est-ce qui vous inspire ?",
                "📚 L'écriture est un super pouvoir ! Vous pourriez écrire sur vos pensées, émotions ou objectifs. Par où commencer ?",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(mot in prompt_lower for mot in ['comment', 'faire']) and any(mot in prompt_lower for mot in ['journal', 'écrire']):
            reponses = [
                "🔧 Pour écrire : Mes Journaux → Nouveau Journal → Écrivez librement ! L'important c'est d'écrire sans se censurer.",
                "💡 Le processus est simple : Mes Journaux → Nouveau → Écrire ! Votre journal est un espace sans jugement.",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(mot in prompt_lower for mot in ['suggestion', 'idée', 'inspiration']):
            reponses = [
                "💡 Idées d'écriture : un souvenir précieux, vos objectifs, ce qui vous rend reconnaissant, ou un défi surmonté.",
                "🎯 Suggestions : décrire votre journée idéale, explorer une émotion, ou écrire à votre futur vous.",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(mot in prompt_lower for mot in ['analyse', 'analyser', 'commente']):
            reponses = [
                "🔍 Je serais ravi d'analyser votre journal ! Sélectionnez d'abord un journal dans la liste à gauche.",
                "📊 L'analyse de journal révèle des patterns intéressants ! Choisissez un journal à explorer.",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(mot in prompt_lower for mot in ['triste', 'heureux', 'stress', 'émotion', 'sentiment']):
            reponses = [
                "💖 Je sens que vous traversez quelque chose. L'écriture peut être un merveilleux exutoire.",
                "🤗 Je comprends que vous ressentez des émotions. Souhaitez-vous en parler à travers l'écriture ?",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(mot in prompt_lower for mot in ['merci', 'thanks', 'remercie']):
            reponses = [
                "🙏 Je vous en prie ! C'est un plaisir de vous accompagner.",
                "😊 Mais de rien ! Continuez votre excellent travail d'écriture.",
            ]
            reponse_text = random.choice(reponses)
        
        elif any(phrase in prompt_lower for phrase in ['ça va', 'comment vas', 'how are you']):
            reponses = [
                "😊 Je vais très bien, merci ! Toujours heureux d'aider avec l'écriture. Et vous ?",
                "🌟 Excellente journée ! Rien ne me rend plus heureux que d'accompagner votre écriture.",
            ]
            reponse_text = random.choice(reponses)
        
        else:
            reponses = [
                f"🤔 '{prompt}'... Intéressant ! Pouvez-vous m'en dire plus ?",
                f"💭 '{prompt}'... Je suis tout ouïe ! Développez un peu.",
                f"🎯 '{prompt}'... Captivant ! Racontez-moi cela en détail.",
            ]
            reponse_text = random.choice(reponses)
        
        return {
            'success': True,
            'reponse': reponse_text,
            'tokens_utilises': len(reponse_text.split()),
            'duree_generation': 0.1,
            'modele_utilise': 'assistant_mindscribe',
        }

class AIServiceManager:
    """Gestionnaire principal du service IA"""
    
    def __init__(self):
        self.openrouter = OpenRouterService()
    
    def traiter_interaction(self, utilisateur, message: str, journal=None, session_id=None, contexte: Dict = None) -> Dict:
        """Traite une interaction utilisateur"""
        
        if not message or len(message.strip()) == 0:
            return {'success': False, 'error': 'Message vide'}
        
        if len(message) > 2000:
            return {'success': False, 'error': 'Message trop long'}
        
        message = message.strip()[:2000]
        start_time = time.time()
        contexte = contexte or {}
        
        try:
            prompt = self._construire_prompt_complet(utilisateur, message, journal, session_id, contexte)
            resultat = self.openrouter.generer_reponse(prompt)
            
            if isinstance(resultat, str):
                resultat = {
                    'success': True,
                    'reponse': resultat,
                    'tokens_utilises': 0,
                    'duree_generation': time.time() - start_time,
                    'modele_utilise': 'simulation',
                }
            
            reponse_complete = resultat.get('reponse') or resultat.get('reponse_fallback', '')
            
            if isinstance(reponse_complete, dict):
                reponse_complete = reponse_complete.get('reponse', '')
            
            type_interaction, reponse_clean = self._analyser_reponse_ia(reponse_complete)
            score_confiance = self._calculer_score_confiance(resultat)
            
            conversation = AssistantIA.objects.create(
                utilisateur=utilisateur,
                journal=journal,
                session_id=session_id,
                message_utilisateur=message,
                reponse_ia=reponse_clean,
                prompt_utilise=prompt,
                statut='termine' if resultat.get('success', True) else 'erreur',
                type_interaction=type_interaction,
                modele_utilise=resultat.get('modele_utilise', 'simulation'),
                tokens_utilises=resultat.get('tokens_utilises', 0),
                duree_generation=time.time() - start_time,
                score_confiance=score_confiance,
            )
            
            return {
                'success': True,
                'conversation_id': str(conversation.id),
                'reponse': conversation.reponse_ia,
                'type_interaction': conversation.type_interaction,
                'date_interaction': conversation.date_creation.strftime('%H:%M'),
                'statistiques': {
                    'tokens_utilises': conversation.tokens_utilises,
                    'duree_generation': conversation.duree_formatee,
                    'score_confiance': conversation.score_confiance
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement interaction: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur lors du traitement: {str(e)}"
            }
     
    def _construire_prompt_complet(self, utilisateur, message: str, journal=None, session_id=None, contexte: Dict = None) -> str:
        """Construit un prompt intelligent"""
        
        prenom = utilisateur.first_name
        nom_affichage = prenom if prenom else utilisateur.username
        
        contexte_journal = ""
        if journal:
            contenu_limite = journal.contenu[:800] + "..." if len(journal.contenu) > 800 else journal.contenu
            contexte_journal = f"""
JOURNAL À ANALYSER:
- Titre: {journal.titre or 'Sans titre'}
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

        prompt = f"""
# CONTEXTE
Utilisateur: {nom_affichage}

{contexte_journal}
{historique}

# INSTRUCTIONS
Tu es MindScribe, assistant expert en écriture de journal.

## TON RÔLE
Analyser la demande et fournir une réponse adaptée.

## TYPES DE RÉPONSES
1. **analyse_journal** - Analyse de texte
2. **suggestion_ecriture** - Idées d'écriture  
3. **support_emotionnel** - Émotions et soutien
4. **accompagnement_pratique** - Aide technique
5. **conversation_naturelle** - Échanges informels

## FORMAT DE RÉPONSE
**TYPE:** [type]
**RÉPONSE:** [ta réponse]

## MESSAGE UTILISATEUR
"{message}"

## TA RÉPONSE:
"""
        return prompt.strip()

    def _analyser_reponse_ia(self, reponse_complete) -> Tuple[str, str]:
        """Analyse la réponse de l'IA"""
        
        if isinstance(reponse_complete, dict):
            reponse_text = reponse_complete.get('reponse') or reponse_complete.get('reponse_fallback', '')
        else:
            reponse_text = str(reponse_complete)
        
        if "**TYPE:**" in reponse_text and "**RÉPONSE:**" in reponse_text:
            try:
                parts = reponse_text.split("**TYPE:**")[1].split("**RÉPONSE:**")
                type_interaction = parts[0].strip().lower()
                reponse_clean = parts[1].strip()
                type_interaction = self._nettoyer_type_interaction(type_interaction)
                return type_interaction, reponse_clean
            except Exception:
                pass
        
        reponse_lower = reponse_text.lower()
        
        if any(mot in reponse_lower for mot in ['analys', 'observation', 'je remarque']):
            type_interaction = 'analyse_journal'
        elif any(mot in reponse_lower for mot in ['suggestion', 'idée', 'conseil']):
            type_interaction = 'suggestion_ecriture'
        elif any(mot in reponse_lower for mot in ['émotion', 'sentiment', 'soutien']):
            type_interaction = 'support_emotionnel'
        elif any(mot in reponse_lower for mot in ['étape', 'procédure', 'comment faire']):
            type_interaction = 'accompagnement_pratique'
        else:
            type_interaction = 'conversation_naturelle'
        
        return type_interaction, reponse_text

    def _nettoyer_type_interaction(self, type_brut: str) -> str:
        """Nettoie le type d'interaction"""
        type_brut = type_brut.lower().strip()
        
        mapping_types = {
            'analyse': 'analyse_journal',
            'suggestion': 'suggestion_ecriture', 
            'support': 'support_emotionnel',
            'accompagnement': 'accompagnement_pratique',
            'conversation': 'conversation_naturelle',
        }
        
        return mapping_types.get(type_brut, 'conversation_naturelle')
    
    def _calculer_score_confiance(self, resultat: Dict) -> float:
        """Calcule un score de confiance"""
        score = 0.5
        
        if not isinstance(resultat, dict):
            return 0.3
        
        if resultat.get('success', False):
            score += 0.3
            if resultat.get('tokens_utilises', 0) > 50:
                score += 0.1
        
        return min(score, 1.0)
    
    def get_statistiques_utilisateur(self, utilisateur):
        """Retourne les statistiques d'utilisation"""
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

# Instance globale
ai_service = AIServiceManager()