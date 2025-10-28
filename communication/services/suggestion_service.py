"""
Enhanced service for generating user connection suggestions based on profile similarity.
Implements sophisticated matching algorithms using user profile data.
"""
import logging
from typing import Dict, List, Optional, Tuple
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from ..models import SuggestionConnexion

logger = logging.getLogger(__name__)

User = get_user_model()


class SuggestionConnexionService:
    """
    Service for generating and managing connection suggestions.
    Uses profile-based similarity matching according to the UML diagram.
    """
    
    # Configuration
    MIN_SIMILARITY_SCORE = 0.25  # Minimum threshold to suggest a connection (lowered for better matching)
    MAX_SUGGESTIONS_PER_USER = 10  # Maximum suggestions to generate per call
    
    # Similarity weights (must sum to 1.0)
    WEIGHTS = {
        'objectif_similaire': 0.40,  # 40% - Most important
        'interet_commun': 0.35,      # 35% - Very important
        'humeur_proche': 0.15,       # 15% - Moderate importance
        'other': 0.10                # 10% - Additional factors
    }
    
    # Mood similarity mapping
    POSITIVE_MOODS = ['heureux']
    NEUTRAL_MOODS = ['neutre']
    NEGATIVE_MOODS = ['triste', 'anxieux', 'stresse']
    
    @classmethod
    def calculate_similarity(cls, user1: User, user2: User) -> Dict:
        """
        Calculate comprehensive similarity score between two users.
        
        Args:
            user1: First user
            user2: Second user
            
        Returns:
            dict: {
                'overall_score': float (0.0-1.0),
                'type': str ('objectif_similaire' | 'humeur_proche' | 'interet_commun'),
                'detailed_scores': {
                    'objectif_similaire': float,
                    'interet_commun': float,
                    'humeur_proche': float,
                    'other': float
                }
            }
        """
        detailed_scores = {}
        
        # 1. OBJECTIFS SIMILAIRES (40% weight)
        obj_score = cls._calculate_objectifs_similarity(user1, user2)
        if obj_score is not None:
            detailed_scores['objectif_similaire'] = obj_score
        
        # 2. CENTRES D'INTÉRÊT (35% weight)
        interest_score = cls._calculate_interests_similarity(user1, user2)
        if interest_score is not None:
            detailed_scores['interet_commun'] = interest_score
        
        # 3. HUMEUR GÉNÉRALE (15% weight)
        mood_score = cls._calculate_mood_similarity(user1, user2)
        if mood_score is not None:
            detailed_scores['humeur_proche'] = mood_score
        
        # 4. AUTRES FACTEURS (10% weight)
        other_score = cls._calculate_other_similarity(user1, user2)
        detailed_scores['other'] = other_score
        
        # Calculate weighted overall score
        overall_score = cls._calculate_weighted_score(detailed_scores)
        
        # Determine primary type (the reason for the suggestion)
        primary_type = cls._determine_primary_type(detailed_scores)
        
        return {
            'overall_score': overall_score,
            'type': primary_type,
            'detailed_scores': detailed_scores
        }
    
    @classmethod
    def _calculate_objectifs_similarity(cls, user1: User, user2: User) -> Optional[float]:
        """Calculate similarity based on personal objectives (Jaccard similarity)."""
        obj1 = set(user1.objectifs_personnels or [])
        obj2 = set(user2.objectifs_personnels or [])
        
        if not obj1 or not obj2:
            return None
        
        intersection = len(obj1 & obj2)
        union = len(obj1 | obj2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    @classmethod
    def _calculate_interests_similarity(cls, user1: User, user2: User) -> Optional[float]:
        """Calculate similarity based on common interests (Jaccard similarity)."""
        int1 = set(user1.centres_interet or [])
        int2 = set(user2.centres_interet or [])
        
        if not int1 or not int2:
            return None
        
        intersection = len(int1 & int2)
        union = len(int1 | int2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    @classmethod
    def _calculate_mood_similarity(cls, user1: User, user2: User) -> Optional[float]:
        """Calculate similarity based on mood/general mood."""
        humeur1 = user1.humeur_generale
        humeur2 = user2.humeur_generale
        
        if not humeur1 or not humeur2:
            return None
        
        # Exact match = perfect score
        if humeur1 == humeur2:
            return 1.0
        
        # Check if moods are in same category
        if (humeur1 in cls.POSITIVE_MOODS and humeur2 in cls.POSITIVE_MOODS) or \
           (humeur1 in cls.NEUTRAL_MOODS and humeur2 in cls.NEUTRAL_MOODS):
            return 0.7
        
        if humeur1 in cls.NEGATIVE_MOODS and humeur2 in cls.NEGATIVE_MOODS:
            return 0.7
        
        # Different categories = lower score
        return 0.3
    
    @classmethod
    def _calculate_other_similarity(cls, user1: User, user2: User) -> float:
        """Calculate similarity based on other factors (profession, passions, etc.)."""
        score = 0.0
        
        # Profession match (30% of other score)
        if user1.profession and user2.profession:
            if user1.profession.lower() == user2.profession.lower():
                score += 0.3
        
        # Passions match (70% of other score)
        passions1 = set(user1.passions or [])
        passions2 = set(user2.passions or [])
        
        if passions1 and passions2:
            intersection = len(passions1 & passions2)
            union = len(passions1 | passions2)
            if union > 0:
                passions_similarity = intersection / union
                score += passions_similarity * 0.7
        
        return min(score, 1.0)
    
    @classmethod
    def _calculate_weighted_score(cls, detailed_scores: Dict[str, float]) -> float:
        """Calculate weighted overall similarity score."""
        total_score = 0.0
        total_weight = 0.0
        
        for key, score in detailed_scores.items():
            if key in cls.WEIGHTS:
                total_score += score * cls.WEIGHTS[key]
                total_weight += cls.WEIGHTS[key]
        
        # If no scores available, return 0
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    @classmethod
    def _determine_primary_type(cls, detailed_scores: Dict[str, float]) -> str:
        """Determine the primary type of suggestion based on highest score."""
        # Default to objectif_similaire
        primary_type = 'objectif_similaire'
        max_score = detailed_scores.get('objectif_similaire', 0.0)
        
        # Check interests
        interest_score = detailed_scores.get('interet_commun', 0.0)
        if interest_score > max_score:
            primary_type = 'interet_commun'
            max_score = interest_score
        
        # Check mood (only if very high, as it's less weighted)
        mood_score = detailed_scores.get('humeur_proche', 0.0)
        if mood_score >= 0.8 and mood_score > max_score * 0.9:  # High mood match can override
            primary_type = 'humeur_proche'
        
        return primary_type
    
    @classmethod
    def generate_suggestions_for_user(cls, user: User, max_suggestions: Optional[int] = None) -> int:
        """
        Generate connection suggestions for a user.
        
        Args:
            user: User to generate suggestions for
            max_suggestions: Maximum number of suggestions to create (default: MAX_SUGGESTIONS_PER_USER)
            
        Returns:
            int: Number of suggestions created
        """
        if max_suggestions is None:
            max_suggestions = cls.MAX_SUGGESTIONS_PER_USER
        
        logger.info(f"🔍 Generating suggestions for user: {user.username}")
        
        # Get all users and filter in Python (Djongo compatibility issue with boolean filters + ordering)
        # Fetch all users without filters/ordering first, then filter in Python
        # This avoids Djongo's issue translating: WHERE is_active ORDER BY date_joined
        try:
            # First try: fetch with is_active filter but clear ordering
            all_users_list = list(User.objects.filter(is_active=True).order_by())
        except Exception as e:
            # Fallback: fetch all users, filter is_active in Python
            logger.warning(f"Query with is_active filter + order_by() failed: {e}. Using fallback.")
            all_users_list = list(User.objects.all())
            # Filter is_active in Python
            all_users_list = [u for u in all_users_list if getattr(u, 'is_active', True) is True]
        
        # Filter out the current user (ensure is_active is still True as a double-check)
        all_other_users = [u for u in all_users_list if u.id != user.id]
        
        # Get users who already have suggestions (convert to list for MongoDB compatibility)
        existing_suggestion_ids = list(SuggestionConnexion.objects.filter(
            utilisateur_source=user
        ).values_list('utilisateur_cible_id', flat=True))
        
        # Filter out users who already have suggestions (done in Python to avoid Djongo issues)
        other_users = [u for u in all_other_users if u.id not in existing_suggestion_ids]
        
        # Calculate similarity for each user
        user_similarities = []
        for other_user in other_users:
            try:
                similarity_data = cls.calculate_similarity(user, other_user)
                overall_score = similarity_data['overall_score']
                
                # Only consider if above minimum threshold
                if overall_score >= cls.MIN_SIMILARITY_SCORE:
                    user_similarities.append({
                        'user': other_user,
                        'score': overall_score,
                        'type': similarity_data['type'],
                        'detailed': similarity_data['detailed_scores']
                    })
            except Exception as e:
                logger.error(f"Error calculating similarity for {other_user.username}: {e}")
                continue
        
        # Sort by score (highest first)
        user_similarities.sort(key=lambda x: x['score'], reverse=True)
        
        # Create suggestions (up to max_suggestions)
        suggestions_created = 0
        for item in user_similarities[:max_suggestions]:
            try:
                # Check again if suggestion already exists (race condition protection)
                if SuggestionConnexion.objects.filter(
                    utilisateur_source=user,
                    utilisateur_cible=item['user']
                ).exists():
                    continue
                
                SuggestionConnexion.objects.create(
                    utilisateur_source=user,
                    utilisateur_cible=item['user'],
                    score_similarite=item['score'],
                    type_suggestion=item['type']
                )
                suggestions_created += 1
                logger.info(
                    f"✅ Created suggestion: {user.username} → {item['user'].username} "
                    f"(score: {item['score']:.2f}, type: {item['type']})"
                )
            except Exception as e:
                logger.error(f"Error creating suggestion for {item['user'].username}: {e}")
                continue
        
        logger.info(f"✨ Generated {suggestions_created} suggestions for {user.username}")
        return suggestions_created
    
    @classmethod
    def get_suggestions_for_user(
        cls, 
        user: User, 
        status: Optional[str] = None,
        limit: Optional[int] = None,
        direction: str = 'all'
    ):
        """
        Get existing suggestions for a user.
        
        Args:
            user: User to get suggestions for
            status: Filter by status ('proposee', 'acceptee', 'ignoree')
            limit: Maximum number of suggestions to return
            direction: 'all', 'sent', or 'received'
            
        Returns:
            QuerySet of SuggestionConnexion objects
        """
        from ..models import SuggestionConnexion
        
        if direction == 'sent':
            queryset = SuggestionConnexion.objects.filter(utilisateur_source=user)
        elif direction == 'received':
            queryset = SuggestionConnexion.objects.filter(utilisateur_cible=user)
        else:  # all
            queryset = SuggestionConnexion.objects.filter(
                Q(utilisateur_source=user) | Q(utilisateur_cible=user)
            )
        
        if status:
            queryset = queryset.filter(statut=status)
        
        queryset = queryset.select_related('utilisateur_source', 'utilisateur_cible')
        queryset = queryset.order_by('-date_suggestion')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @classmethod
    def recalculate_suggestion_score(cls, suggestion: SuggestionConnexion) -> SuggestionConnexion:
        """
        Recalculate similarity score for an existing suggestion.
        Useful when user profiles are updated.
        
        Args:
            suggestion: SuggestionConnexion instance to update
            
        Returns:
            Updated SuggestionConnexion instance
        """
        similarity_data = cls.calculate_similarity(
            suggestion.utilisateur_source,
            suggestion.utilisateur_cible
        )
        
        suggestion.score_similarite = similarity_data['overall_score']
        suggestion.type_suggestion = similarity_data['type']
        suggestion.save()
        
        logger.info(f"🔄 Recalculated suggestion {suggestion.id}: score={similarity_data['overall_score']:.2f}")
        return suggestion

