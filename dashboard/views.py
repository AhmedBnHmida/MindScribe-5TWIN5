# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from analysis.models import AnalyseIA
from journal.models import Journal
from datetime import datetime, timedelta
from collections import Counter
import json

from django.views.decorators.http import require_http_methods
from .models import BilanMensuel, Statistique
from .services import ServiceBilanIA


@login_required
def tableau_bord(request):
    """Vue principale du tableau de bord"""
    return render(request, 'dashboard/dashboard.html')

# ==================== APIs pour les données ====================

@login_required
def donnees_evolution_humeur(request):
    """API pour les données du graphique d'évolution d'humeur"""
    analyses = AnalyseIA.objects.filter(
        journal__utilisateur=request.user
    ).select_related('journal').order_by('journal__date_creation')
    
    dates = []
    scores = []
    tons = []
    
    for analyse in analyses:
        # Convertir le ton en score numérique
        score_map = {'positif': 1, 'neutre': 0, 'negatif': -1}
        
        dates.append(analyse.journal.date_creation.strftime('%Y-%m-%d'))
        scores.append(score_map.get(analyse.ton_general, 0))
        tons.append(analyse.ton_general)
    
    return JsonResponse({
        'dates': dates,
        'scores': scores,
        'tons': tons
    })

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
    
    # Formate pour le word cloud
    wordcloud_data = [[mot, count] for mot, count in frequences.most_common(50)]
    
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
        'data': data
    })

@login_required
def donnees_chronologie(request):
    """API pour les données de la chronologie"""
    analyses = AnalyseIA.objects.filter(
        journal__utilisateur=request.user
    ).select_related('journal').order_by('-journal__date_creation')[:10]
    
    events = []
    for analyse in analyses:
        # Détermine la couleur selon le ton
        couleur_map = {
            'positif': '#10b981',
            'neutre': '#f59e0b', 
            'negatif': '#ef4444'
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
            'ton': analyse.ton_general,
            'mots_cles': analyse.mots_cles[:3]
        })
    
    return JsonResponse({'events': events})

@login_required
def donnees_statistiques(request):
    """API pour les statistiques globales"""
    analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
    total_analyses = analyses.count()
    
    # Calcul de l'humeur moyenne
    tons = list(analyses.values_list('ton_general', flat=True))
    ton_counts = Counter(tons)
    
    if tons:
        humeur_moyenne = max(ton_counts, key=ton_counts.get)
    else:
        humeur_moyenne = 'neutre'
    
    # Thèmes uniques
    tous_themes = []
    for analyse in analyses:
        tous_themes.extend(analyse.themes_detectes)
    themes_uniques = len(set(tous_themes))
    
    # Mots-clés uniques
    tous_mots_cles = []
    for analyse in analyses:
        tous_mots_cles.extend(analyse.mots_cles)
    mots_cles_uniques = len(set(tous_mots_cles))
    
    return JsonResponse({
        'total_analyses': total_analyses,
        'humeur_moyenne': humeur_moyenne,
        'themes_uniques': themes_uniques,
        'mots_cles': mots_cles_uniques
    })

@login_required
def donnees_distribution_humeurs(request):
    """API pour la distribution des humeurs"""
    analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
    
    ton_counts = Counter(analyses.values_list('ton_general', flat=True))
    
    return JsonResponse({
        'positif': ton_counts.get('positif', 0),
        'neutre': ton_counts.get('neutre', 0),
        'negatif': ton_counts.get('negatif', 0)
    })

@login_required
def donnees_frequence_ecriture(request):
    """API pour la fréquence d'écriture"""
    journaux = Journal.objects.filter(utilisateur=request.user).order_by('date_creation')
    
    # Group par date (simplifié)
    dates_count = {}
    for journal in journaux:
        date_str = journal.date_creation.strftime('%Y-%m-%d')
        dates_count[date_str] = dates_count.get(date_str, 0) + 1
    
    # Limiter aux 30 derniers jours pour la démo
    sorted_dates = sorted(dates_count.keys())[-30:]
    
    return JsonResponse({
        'dates': sorted_dates,
        'counts': [dates_count[date] for date in sorted_dates]
    })

@login_required
def donnees_score_emotionnel(request):
    """API pour le score émotionnel (données simulées pour la démo)"""
    return JsonResponse({
        'scores': [75, 60, 80, 55, 70]  # Positivité, Stabilité, Intensité, Diversité, Croissance
    })






@login_required
def bilan_mensuel(request, annee=None, mois=None):
    """Vue pour afficher les bilans mensuels"""
    aujourdhui = datetime.now()
    annee = annee or aujourdhui.year
    mois = mois or aujourdhui.month
    
    periode = f"{mois:02d}/{annee}"
    
    # Récupère ou génère le bilan
    try:
        statistique = Statistique.objects.get(
            utilisateur=request.user,
            periode=periode
        )
        try:
            bilan = BilanMensuel.objects.get(statistique=statistique)
        except BilanMensuel.DoesNotExist:
            # Génère le bilan automatiquement
            bilan = ServiceBilanIA.generer_bilan_mensuel(request.user, mois, annee)
    except Statistique.DoesNotExist:
        # Génère la statistique et le bilan
        bilan = ServiceBilanIA.generer_bilan_mensuel(request.user, mois, annee)
    
    # Récupère l'historique des bilans
    bilans_historique = BilanMensuel.objects.filter(
        utilisateur=request.user
    ).select_related('statistique').order_by('-date_creation')[:12]
    
    context = {
        'bilan': bilan,
        'bilans_historique': bilans_historique,
        'annee_courante': annee,
        'mois_courant': mois,
        'periode': periode
    }
    
    return render(request, 'dashboard/bilan_mensuel.html', context)

@login_required
@require_http_methods(["POST"])
def generer_bilan_api(request):
    """API pour générer un bilan mensuel"""
    try:
        data = json.loads(request.body)
        mois = int(data.get('mois', datetime.now().month))
        annee = int(data.get('annee', datetime.now().year))
        
        bilan = ServiceBilanIA.generer_bilan_mensuel(request.user, mois, annee)
        
        return JsonResponse({
            'success': True,
            'bilan_id': str(bilan.id),
            'titre': bilan.titre,
            'resume': bilan.resume,
            'statut': bilan.statut
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)