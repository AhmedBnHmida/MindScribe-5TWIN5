from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from .models import Journal
from analysis.models import AnalyseIA
from module2_analysis.models import JournalAnalysis

@login_required
def create_journal_entry(request):
    """
    View for creating a new journal entry with multimodal content
    """
    return render(request, 'journal/create_entry.html')

@login_required
def journal_list(request):
    """
    View for listing user's journal entries from both old and new systems with pagination and search
    """
    # Get search query and filter type
    search_query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', 'all')
    
    # Get entries from old Journal model
    old_journals = Journal.objects.filter(utilisateur=request.user)
    
    # Get entries from new JournalAnalysis model
    new_journals = JournalAnalysis.objects.filter(user=request.user)
    
    # Apply search filter to new journals
    if search_query:
        new_journals = new_journals.filter(
            Q(text__icontains=search_query) |
            Q(summary__icontains=search_query) |
            Q(audio_transcription__icontains=search_query) |
            Q(keywords__icontains=search_query)
        )
        
        old_journals = old_journals.filter(
            Q(contenu__icontains=search_query)
        )
    
    # Apply type filter
    if filter_type == 'text':
        new_journals = new_journals.exclude(text='').exclude(text__isnull=True)
        old_journals = old_journals  # Old journals are all text
    elif filter_type == 'audio':
        new_journals = new_journals.exclude(audio_file='').exclude(audio_file__isnull=True)
        old_journals = old_journals.none()  # No audio in old journals
    elif filter_type == 'image':
        new_journals = new_journals.exclude(image_file='').exclude(image_file__isnull=True)
        old_journals = old_journals.none()  # No images in old journals
    
    # Order by date
    old_journals = old_journals.order_by('-date_creation')
    new_journals = new_journals.order_by('-created_at')
    
    # Combine and sort both querysets by date
    # We need to convert them to lists and combine them
    all_entries = sorted(
        chain(new_journals, old_journals),
        key=lambda x: x.created_at if hasattr(x, 'created_at') else x.date_creation,
        reverse=True
    )
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(all_entries, 10)  # Show 10 entries per page
    
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    
    return render(request, 'journal/journal_list.html', {
        'entries': entries,
        'search_query': search_query,
        'filter_type': filter_type,
        'total_count': len(all_entries)
    })

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

@login_required
def edit_journal(request, journal_id):
    """
    View for editing a new journal analysis entry and rerunning AI analysis
    """
    from module2_analysis.services import analyze_multimodal_content
    import os
    
    entry = get_object_or_404(JournalAnalysis, id=journal_id, user=request.user)
    
    if request.method == 'POST':
        text = request.POST.get('text', '')
        
        # Update the text
        entry.text = text
        
        # Prepare paths for audio and image if they exist
        audio_path = None
        image_path = None
        
        if entry.audio_file:
            audio_path = entry.audio_file.path
        
        if entry.image_file:
            image_path = entry.image_file.path
        
        try:
            # Rerun AI analysis with updated content
            analysis_results = analyze_multimodal_content(
                text=text if text else None,
                audio_path=audio_path,
                image_path=image_path
            )
            
            # Update all analysis fields
            entry.sentiment = analysis_results.get('sentiment', 'neutre')
            entry.emotion_score = analysis_results.get('emotion_score', 0.5)
            entry.emotions_detected = analysis_results.get('emotions_detected') or []
            entry.keywords = analysis_results.get('keywords') or []
            entry.topics = analysis_results.get('topics') or []
            entry.summary = analysis_results.get('summary', '')
            entry.detailed_summary = analysis_results.get('detailed_summary', '')
            entry.positive_aspects = analysis_results.get('positive_aspects') or []
            entry.negative_aspects = analysis_results.get('negative_aspects') or []
            entry.action_items = analysis_results.get('action_items') or []
            entry.mood_analysis = analysis_results.get('mood_analysis', '')
            
            # Keep existing transcription/captions (don't overwrite from analysis)
            if not entry.audio_transcription and analysis_results.get('audio_transcription'):
                entry.audio_transcription = analysis_results.get('audio_transcription')
            
            if not entry.image_caption and analysis_results.get('image_caption'):
                entry.image_caption = analysis_results.get('image_caption')
                entry.image_scene = analysis_results.get('image_scene', '')
                entry.image_analysis = analysis_results.get('image_analysis', '')
            
            entry.save()
            
            messages.success(request, 'Entrée modifiée et analyse IA mise à jour avec succès!')
        except Exception as e:
            # If analysis fails, still save the text changes
            entry.save()
            messages.warning(request, f'Entrée modifiée mais l\'analyse IA a échoué: {str(e)}')
        
        return redirect('journal:list')
    
    return render(request, 'journal/edit_entry.html', {
        'entry': entry
    })

@login_required
def edit_old_journal(request, journal_id):
    """
    View for editing an old journal entry
    """
    journal = get_object_or_404(Journal, id=journal_id, utilisateur=request.user)
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu', '')
        
        # Update the journal
        journal.contenu = contenu
        journal.save()
        
        messages.success(request, 'Entrée modifiée avec succès!')
        return redirect('journal:list')
    
    return render(request, 'journal/edit_old_entry.html', {
        'journal': journal
    })

@login_required
@require_POST
def delete_journal(request, journal_id):
    """
    View for deleting a new journal analysis entry
    """
    entry = get_object_or_404(JournalAnalysis, id=journal_id, user=request.user)
    entry.delete()
    
    messages.success(request, 'Entrée supprimée avec succès!')
    return redirect('journal:list')

@login_required
@require_POST
def delete_old_journal(request, journal_id):
    """
    View for deleting an old journal entry
    """
    journal = get_object_or_404(Journal, id=journal_id, utilisateur=request.user)
    journal.delete()
    
    messages.success(request, 'Entrée supprimée avec succès!')
    return redirect('journal:list')
