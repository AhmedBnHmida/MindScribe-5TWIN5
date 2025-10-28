"""
Django signals for automatic recommendation generation.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from module2_analysis.models import JournalAnalysis
from .models import Recommandation
from .services import create_recommendations_for_user, get_user_analysis_summary

logger = logging.getLogger(__name__)


@receiver(post_save, sender=JournalAnalysis)
def trigger_recommendations_on_journal_entry(sender, instance, created, **kwargs):
    """
    Automatically generate recommendations when certain conditions are met.
    
    Conditions for automatic generation:
    1. User has 3+ journal entries in the last 7 days
    2. User hasn't received recommendations in the last 2 days
    3. There's a significant emotional pattern detected
    """
    if not created:
        return  # Only trigger on new entries
    
    try:
        user = instance.user
        
        # Check if user has enough recent entries
        week_ago = timezone.now() - timedelta(days=7)
        recent_entries_count = JournalAnalysis.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).count()
        
        if recent_entries_count < 3:
            logger.info(f"User {user.username} has only {recent_entries_count} entries, skipping auto-recommendations")
            return
        
        # Check if user already has recent recommendations
        two_days_ago = timezone.now() - timedelta(days=2)
        recent_recommendations = Recommandation.objects.filter(
            utilisateur=user,
            date_emission__gte=two_days_ago
        ).exists()
        
        if recent_recommendations:
            logger.info(f"User {user.username} already has recent recommendations, skipping")
            return
        
        # Get user's analysis summary
        summary = get_user_analysis_summary(user, days=7)
        
        # Check for significant patterns that warrant recommendations
        should_generate = False
        
        # Trigger 1: Negative trend detected
        if summary['trend'] == 'declining':
            should_generate = True
            logger.info(f"Negative trend detected for {user.username}, generating recommendations")
        
        # Trigger 2: Low average emotion score
        elif summary['average_emotion_score'] < 0.4:
            should_generate = True
            logger.info(f"Low emotion score for {user.username}, generating recommendations")
        
        # Trigger 3: High negative sentiment ratio
        elif summary['sentiment_distribution']:
            total = sum(summary['sentiment_distribution'].values())
            negative_ratio = summary['sentiment_distribution'].get('negatif', 0) / total if total > 0 else 0
            if negative_ratio > 0.5:
                should_generate = True
                logger.info(f"High negative sentiment for {user.username}, generating recommendations")
        
        # Trigger 4: Milestone reached (every 5th entry)
        elif recent_entries_count % 5 == 0:
            should_generate = True
            logger.info(f"Milestone reached for {user.username} ({recent_entries_count} entries), generating recommendations")
        
        # Generate recommendations if conditions are met
        if should_generate:
            recommendations = create_recommendations_for_user(user)
            logger.info(f"Auto-generated {len(recommendations)} recommendations for {user.username}")
        
    except Exception as e:
        logger.error(f"Error in auto-recommendation signal: {e}", exc_info=True)


@receiver(post_save, sender=Recommandation)
def log_recommendation_creation(sender, instance, created, **kwargs):
    """Log when a new recommendation is created."""
    if created:
        logger.info(f"New recommendation created: {instance.type} for {instance.utilisateur.username}")


def check_user_goals_progress(user):
    """
    Check user's goals and generate motivational recommendations.
    This function can be called by a scheduled task (Celery).
    """
    from .models import Objectif
    
    try:
        active_goals = Objectif.objects.filter(
            utilisateur=user,
            date_fin__gte=timezone.now().date(),
            progres__lt=100
        )
        
        for goal in active_goals:
            # Check if goal is nearing deadline with low progress
            days_remaining = (goal.date_fin - timezone.now().date()).days
            
            if days_remaining <= 7 and goal.progres < 50:
                # Create motivational recommendation
                Recommandation.objects.create(
                    utilisateur=user,
                    type='productivite',
                    contenu=f"Ton objectif '{goal.nom}' se termine dans {days_remaining} jours. Tu as fait {goal.progres:.0f}% du chemin. Continue, tu peux le faire ! 💪",
                    statut='nouvelle'
                )
                logger.info(f"Created goal reminder for {user.username}: {goal.nom}")
            
            # Celebrate goals nearing completion
            elif goal.progres >= 80 and goal.progres < 100:
                # Check if we already sent a celebration message
                recent_celebration = Recommandation.objects.filter(
                    utilisateur=user,
                    contenu__icontains=goal.nom,
                    date_emission__gte=timezone.now() - timedelta(days=5)
                ).exists()
                
                if not recent_celebration:
                    Recommandation.objects.create(
                        utilisateur=user,
                        type='bien_etre',
                        contenu=f"Bravo ! Tu es à {goal.progres:.0f}% de ton objectif '{goal.nom}'. Plus que quelques efforts ! 🎯",
                        statut='nouvelle'
                    )
                    logger.info(f"Created celebration message for {user.username}: {goal.nom}")
    
    except Exception as e:
        logger.error(f"Error checking goals progress: {e}", exc_info=True)

