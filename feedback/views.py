from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Feedback, FeedbackModalDismissal
from module2_analysis.models import JournalAnalysis
from journal.models import Journal


@login_required
def feedback_list(request):
    """
    Display all feedbacks for the current user with CRUD options
    """
    feedbacks = Feedback.objects.filter(user=request.user)
    
    context = {
        'feedbacks': feedbacks
    }
    
    return render(request, 'feedback/feedback_list.html', context)


@login_required
@require_POST
def create_feedback(request):
    """
    Create a new feedback entry
    """
    rating = request.POST.get('rating')
    feedback_text = request.POST.get('feedback_text', '')
    
    if not rating:
        messages.error(request, 'Veuillez sélectionner une note.')
        return redirect('feedback:list')
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        feedback = Feedback.objects.create(
            user=request.user,
            rating=rating,
            feedback_text=feedback_text
        )
        
        messages.success(request, 'Merci pour votre retour ! 🎉')
        
        # Check if this was from the modal (via AJAX)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Merci pour votre retour !'
            })
        
        return redirect('feedback:list')
        
    except (ValueError, TypeError) as e:
        messages.error(request, 'Note invalide. Veuillez réessayer.')
        return redirect('feedback:list')


@login_required
def edit_feedback(request, feedback_id):
    """
    Edit an existing feedback entry
    """
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text', '')
        
        if not rating:
            messages.error(request, 'Veuillez sélectionner une note.')
            return redirect('feedback:edit', feedback_id=feedback_id)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            
            feedback.rating = rating
            feedback.feedback_text = feedback_text
            feedback.save()
            
            messages.success(request, 'Votre retour a été modifié avec succès !')
            return redirect('feedback:list')
            
        except (ValueError, TypeError):
            messages.error(request, 'Note invalide. Veuillez réessayer.')
            return redirect('feedback:edit', feedback_id=feedback_id)
    
    return render(request, 'feedback/edit_feedback.html', {
        'feedback': feedback
    })


@login_required
@require_POST
def delete_feedback(request, feedback_id):
    """
    Delete a feedback entry
    """
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    feedback.delete()
    
    messages.success(request, 'Votre retour a été supprimé.')
    return redirect('feedback:list')


@login_required
@require_POST
def dismiss_modal(request):
    """
    Record when user dismisses the feedback modal
    """
    # Count user's journals
    journal_count = Journal.objects.filter(utilisateur=request.user).count()
    analysis_count = JournalAnalysis.objects.filter(user=request.user).count()
    total_count = journal_count + analysis_count
    
    FeedbackModalDismissal.objects.create(
        user=request.user,
        journal_count_at_dismissal=total_count
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('journal:list')


@login_required
def check_should_show_modal(request):
    """
    API endpoint to check if the feedback modal should be shown
    Returns JSON with should_show boolean
    """
    # Count user's journals
    journal_count = Journal.objects.filter(utilisateur=request.user).count()
    analysis_count = JournalAnalysis.objects.filter(user=request.user).count()
    total_count = journal_count + analysis_count
    
    # Check if user has 5 or more journals
    if total_count < 5:
        return JsonResponse({'should_show': False, 'reason': 'not_enough_journals'})
    
    # Check if user already gave feedback
    has_feedback = Feedback.objects.filter(user=request.user).exists()
    if has_feedback:
        return JsonResponse({'should_show': False, 'reason': 'already_provided_feedback'})
    
    # Check if user dismissed the modal recently (within last 10 journals)
    last_dismissal = FeedbackModalDismissal.objects.filter(user=request.user).first()
    if last_dismissal:
        journals_since_dismissal = total_count - last_dismissal.journal_count_at_dismissal
        if journals_since_dismissal < 10:
            return JsonResponse({
                'should_show': False,
                'reason': 'recently_dismissed',
                'journals_until_next': 10 - journals_since_dismissal
            })
    
    # All conditions met, show the modal
    return JsonResponse({'should_show': True, 'journal_count': total_count})
