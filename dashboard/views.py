from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from analysis.models import AnalyseIA
from django.http import JsonResponse
from datetime import datetime, timedelta
from collections import Counter
import json

@login_required
def tableau_bord(request):
    """Vue principale du tableau de bord"""
    return render(request, 'dashboard/dashboard.html')

@login_required
def donnees_evolution_humeur(request):
    """API pour les données du graphique d'évolution d'humeur"""
    analyses = AnalyseIA.objects.filter(
        journal__utilisateur=request.user
    ).select_related('journal').order_by('journal__date_creation')
    
    data = []
    for analyse in analyses:
        # Convertir le ton en score numérique pour le graphique
        score_map = {'positif': 1, 'neutre': 0, 'negatif': -1}
        
        data.append({
            'date': analyse.journal.date_creation.strftime('%Y-%m-%d'),
            'score': score_map[analyse.ton_general],
            'ton': analyse.ton_general,
            'themes': analyse.themes_detectes[:3]  # 3 premiers thèmes
        })
    
    return JsonResponse({'data': data})

@login_required
def donnees_wordcloud(request):
    """API pour les données du word cloud"""
    analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
    
    # Agrège tous les mots-clés
    tous_mots_cles = []
    for analyse in analyses:
        tous_mots_cles.extend(analyse.mots_cles)
    
    # Calcule les fréquences
    frequences = Counter(tous_mots_cles)
    
    # Formate pour le word cloud (mot: fréquence)
    wordcloud_data = [{'text': mot, 'value': count} for mot, count in frequences.most_common(50)]
    
    return JsonResponse({'wordcloud': wordcloud_data})

@login_required
def donnees_themes(request):
    """API pour les données des thèmes dominants"""
    analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
    
    # Agrège tous les thèmes
    tous_themes = []
    for analyse in analyses:
        tous_themes.extend(analyse.themes_detectes)
    
    # Compte les occurrences
    themes_comptes = Counter(tous_themes).most_common(10)
    
    # Prépare les données pour le graphique
    labels = [theme for theme, count in themes_comptes]
    data = [count for theme, count in themes_comptes]
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'total_themes': len(tous_themes)
    })

@login_required
def donnees_chronologie(request):
    """API pour les données de la chronologie"""
    analyses = AnalyseIA.objects.filter(
        journal__utilisateur=request.user
    ).select_related('journal').order_by('-journal__date_creation')[:20]  # 20 derniers
    
    events = []
    for analyse in analyses:
        # Détermine l'icône et la couleur selon le ton
        couleur_map = {
            'positif': '#10b981',  # Vert
            'neutre': '#6b7280',   # Gris
            'negatif': '#ef4444'   # Rouge
        }
        
        icone_map = {
            'positif': '😊',
            'neutre': '😐', 
            'negatif': '😞'
        }
        
        events.append({
            'date': analyse.journal.date_creation.strftime('%d %b %Y'),
            'titre': f"{icone_map[analyse.ton_general]} Humeur {analyse.ton_general}",
            'description': f"Thèmes: {', '.join(analyse.themes_detectes[:2])}",
            'couleur': couleur_map[analyse.ton_general],
            'mots_cles': analyse.mots_cles[:3]
        })
    
    return JsonResponse({'events': events})