"""
Views for the recommendations module.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Recommandation, Objectif
from .services import (
    create_recommendations_for_user,
    get_user_recommendations,
    mark_recommendation_status,
    get_user_analysis_summary
)

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """
    Main dashboard view for recommendations and goals.
    """
    user = request.user
    
    try:
        # Get recent recommendations
        recent_recommendations = list(get_user_recommendations(user, limit=10))
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        recent_recommendations = []
    
    try:
        # Get new recommendations count
        new_count = Recommandation.objects.filter(
            utilisateur=user,
            statut='nouvelle'
        ).count()
    except Exception as e:
        logger.error(f"Error counting new recommendations: {e}")
        new_count = 0
    
    try:
        # Get user's active goals - filter in Python to avoid Djongo date issues
        all_goals = Objectif.objects.filter(utilisateur=user).order_by('-date_creation')
        today = timezone.now().date()
        active_goals = [goal for goal in all_goals if goal.date_fin >= today][:5]
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        active_goals = []
    
    try:
        # Get user's analysis summary
        summary = get_user_analysis_summary(user, days=7)
    except Exception as e:
        logger.error(f"Error getting analysis summary: {e}")
        summary = {
            'total_entries': 0,
            'sentiment_distribution': {},
            'common_emotions': [],
            'common_keywords': [],
            'common_topics': [],
            'average_emotion_score': 0,
            'trend': 'insufficient_data'
        }
    
    try:
        # Calculate recommendation statistics
        total_recommendations = Recommandation.objects.filter(utilisateur=user).count()
        followed_count = Recommandation.objects.filter(
            utilisateur=user,
            statut='suivie'
        ).count()
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        total_recommendations = 0
        followed_count = 0
    
    context = {
        'recommendations': recent_recommendations,
        'new_recommendations_count': new_count,
        'active_goals': active_goals,
        'summary': summary,
        'total_recommendations': total_recommendations,
        'followed_count': followed_count,
        'follow_rate': (followed_count / total_recommendations * 100) if total_recommendations > 0 else 0,
    }
    
    return render(request, 'recommendations/dashboard.html', context)


@login_required
@require_POST
def generate_recommendations(request):
    """
    Generate new recommendations for the user.
    """
    try:
        recommendations = create_recommendations_for_user(request.user)
        
        if recommendations:
            messages.success(
                request,
                f"✨ {len(recommendations)} nouvelles recommandations générées avec succès !"
            )
        else:
            messages.info(
                request,
                "Aucune nouvelle recommandation pour le moment. Continue à écrire dans ton journal !"
            )
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        messages.error(
            request,
            "Une erreur est survenue lors de la génération des recommandations."
        )
    
    return redirect('recommendations:dashboard')


@login_required
@require_POST
def update_recommendation_status(request, recommendation_id):
    """
    Update the status of a recommendation (AJAX endpoint).
    """
    status = request.POST.get('status')
    
    if status not in ['suivie', 'ignoree']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    recommendation = get_object_or_404(
        Recommandation,
        id=recommendation_id,
        utilisateur=request.user
    )
    
    recommendation.statut = status
    recommendation.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Statut mis à jour',
        'new_status': status
    })


@login_required
def recommendations_list(request):
    """
    List all recommendations with filtering options.
    """
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')
    
    # Base queryset
    recommendations = Recommandation.objects.filter(utilisateur=user)
    
    # Apply filters
    if status_filter != 'all':
        recommendations = recommendations.filter(statut=status_filter)
    
    if type_filter != 'all':
        recommendations = recommendations.filter(type=type_filter)
    
    # Order by date
    recommendations = recommendations.order_by('-date_emission')
    
    # Get statistics for each type
    type_stats = {}
    for type_choice, type_label in Recommandation.TYPE_CHOICES:
        count = Recommandation.objects.filter(
            utilisateur=user,
            type=type_choice
        ).count()
        type_stats[type_choice] = {
            'label': type_label,
            'count': count
        }
    
    context = {
        'recommendations': recommendations,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'type_stats': type_stats,
    }
    
    return render(request, 'recommendations/list.html', context)


@login_required
def goals_list(request):
    """
    List all user goals.
    """
    user = request.user
    
    try:
        # Get all goals and filter in Python to avoid Djongo issues
        all_goals = list(Objectif.objects.filter(utilisateur=user))
        today = timezone.now().date()
        
        # Active goals: not expired and not completed
        active_goals = sorted(
            [g for g in all_goals if g.date_fin >= today and g.progres < 100],
            key=lambda x: x.date_fin
        )
        
        # Completed goals: progress >= 100
        completed_goals = sorted(
            [g for g in all_goals if g.progres >= 100],
            key=lambda x: x.date_mise_a_jour,
            reverse=True
        )[:10]
        
        # Expired goals: past deadline and not completed
        expired_goals = sorted(
            [g for g in all_goals if g.date_fin < today and g.progres < 100],
            key=lambda x: x.date_fin,
            reverse=True
        )[:10]
        
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        active_goals = []
        completed_goals = []
        expired_goals = []
    
    context = {
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'expired_goals': expired_goals,
    }
    
    return render(request, 'recommendations/goals.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_goal(request):
    """
    Create a new goal.
    """
    if request.method == 'POST':
        try:
            goal = Objectif.objects.create(
                utilisateur=request.user,
                nom=request.POST.get('nom'),
                description=request.POST.get('description', ''),
                date_debut=request.POST.get('date_debut'),
                date_fin=request.POST.get('date_fin'),
                progres=0.0
            )
            
            messages.success(request, f"🎯 Objectif '{goal.nom}' créé avec succès !")
            return redirect('recommendations:goals')
            
        except Exception as e:
            logger.error(f"Error creating goal: {e}")
            messages.error(request, "Erreur lors de la création de l'objectif.")
            return redirect('recommendations:goals')
    
    return render(request, 'recommendations/create_goal.html')


@login_required
@require_POST
def update_goal_progress(request, goal_id):
    """
    Update the progress of a goal (AJAX endpoint).
    """
    goal = get_object_or_404(Objectif, id=goal_id, utilisateur=request.user)
    
    try:
        progress = float(request.POST.get('progress', 0))
        progress = max(0, min(100, progress))  # Clamp between 0 and 100
        
        goal.progres = progress
        goal.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Progrès mis à jour',
            'progress': progress,
            'is_completed': goal.est_termine
        })
    except ValueError:
        return JsonResponse({'error': 'Invalid progress value'}, status=400)


@login_required
def goal_detail(request, goal_id):
    """
    Detailed view for tracking a single goal.
    """
    goal = get_object_or_404(Objectif, id=goal_id, utilisateur=request.user)
    
    # Calculate days remaining
    today = timezone.now().date()
    days_remaining = (goal.date_fin - today).days
    days_elapsed = (today - goal.date_debut).days
    total_days = (goal.date_fin - goal.date_debut).days
    
    context = {
        'goal': goal,
        'days_remaining': days_remaining,
        'days_elapsed': days_elapsed,
        'total_days': total_days,
        'is_overdue': days_remaining < 0,
    }
    
    return render(request, 'recommendations/goal_detail.html', context)


@login_required
@require_POST
def delete_goal(request, goal_id):
    """
    Delete a goal.
    """
    goal = get_object_or_404(Objectif, id=goal_id, utilisateur=request.user)
    goal_name = goal.nom
    goal.delete()
    
    messages.success(request, f"Objectif '{goal_name}' supprimé.")
    return redirect('recommendations:goals')



