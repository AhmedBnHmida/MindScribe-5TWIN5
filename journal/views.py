from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Journal
from analysis.models import AnalyseIA

@login_required
def create_journal_entry(request):
    """
    View for creating a new journal entry with multimodal content
    """
    return render(request, 'journal/create_entry.html')

@login_required
def journal_list(request):
    """
    View for listing user's journal entries
    """
    journals = Journal.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'journal/journal_list.html', {'journals': journals})

@login_required
def journal_detail(request, journal_id):
    """
    View for displaying a journal entry and its analysis
    """
    journal = get_object_or_404(Journal, id=journal_id, utilisateur=request.user)
    
    # Try to get the associated analysis
    try:
        analyse = journal.analyse
    except AnalyseIA.DoesNotExist:
        analyse = None
    
    return render(request, 'journal/journal_detail.html', {
        'journal': journal,
        'analyse': analyse
    })
