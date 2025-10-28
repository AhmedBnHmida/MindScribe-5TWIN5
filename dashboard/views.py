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
from .services.analyse_ia import AnalyseurRapide
from .models import BilanMensuel, Statistique, AnalyseRapide  # Ajouter AnalyseRapide

@login_required
def tableau_bord(request):
    """Vue principale du tableau de bord"""
    return render(request, 'dashboard/dashboard.html')


# ==================== APIs pour les données ====================

@login_required
def donnees_evolution_humeur(request):
    """API pour les données du graphique d'évolution d'humeur"""
    try:
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
            'success': True,
            'dates': dates,
            'scores': scores,
            'tons': tons
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_wordcloud(request):
    """API pour les données du word cloud"""
    try:
        analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
        
        # Agrège tous les mots-clés
        tous_mots_cles = []
        for analyse in analyses:
            if analyse.mots_cles:
                tous_mots_cles.extend(analyse.mots_cles)
        
        # Calcule les fréquences
        frequences = Counter(tous_mots_cles)
        
        # Formate pour le word cloud
        wordcloud_data = [[mot, count] for mot, count in frequences.most_common(50)]
        
        return JsonResponse({
            'success': True,
            'wordcloud': wordcloud_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_themes(request):
    """API pour les données des thèmes dominants"""
    try:
        analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
        
        # Agrège tous les thèmes
        tous_themes = []
        for analyse in analyses:
            if analyse.themes_detectes:
                tous_themes.extend(analyse.themes_detectes)
        
        # Compte les occurrences
        themes_comptes = Counter(tous_themes).most_common(10)
        
        # Prépare les données pour le graphique
        labels = [theme for theme, count in themes_comptes]
        data = [count for theme, count in themes_comptes]
        
        return JsonResponse({
            'success': True,
            'labels': labels,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_chronologie(request):
    """API pour les données de la chronologie"""
    try:
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
                'titre': f"{icone_map.get(analyse.ton_general, '😐')} Humeur {analyse.ton_general}",
                'description': f"Thèmes: {', '.join(analyse.themes_detectes[:2]) if analyse.themes_detectes else 'Aucun'}",
                'couleur': couleur_map.get(analyse.ton_general, '#f59e0b'),
                'ton': analyse.ton_general,
                'mots_cles': analyse.mots_cles[:3] if analyse.mots_cles else []
            })
        
        return JsonResponse({
            'success': True,
            'events': events
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_statistiques(request):
    """API pour les statistiques globales"""
    try:
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
            if analyse.themes_detectes:
                tous_themes.extend(analyse.themes_detectes)
        themes_uniques = len(set(tous_themes))
        
        # Mots-clés uniques
        tous_mots_cles = []
        for analyse in analyses:
            if analyse.mots_cles:
                tous_mots_cles.extend(analyse.mots_cles)
        mots_cles_uniques = len(set(tous_mots_cles))
        
        return JsonResponse({
            'success': True,
            'total_analyses': total_analyses,
            'humeur_moyenne': humeur_moyenne,
            'themes_uniques': themes_uniques,
            'mots_cles': mots_cles_uniques
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_distribution_humeurs(request):
    """API pour la distribution des humeurs"""
    try:
        analyses = AnalyseIA.objects.filter(journal__utilisateur=request.user)
        
        ton_counts = Counter(analyses.values_list('ton_general', flat=True))
        
        return JsonResponse({
            'success': True,
            'positif': ton_counts.get('positif', 0),
            'neutre': ton_counts.get('neutre', 0),
            'negatif': ton_counts.get('negatif', 0)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_frequence_ecriture(request):
    """API pour la fréquence d'écriture"""
    try:
        journaux = Journal.objects.filter(utilisateur=request.user).order_by('date_creation')
        
        # Group par date (simplifié)
        dates_count = {}
        for journal in journaux:
            date_str = journal.date_creation.strftime('%Y-%m-%d')
            dates_count[date_str] = dates_count.get(date_str, 0) + 1
        
        # Limiter aux 30 derniers jours pour la démo
        sorted_dates = sorted(dates_count.keys())[-30:]
        
        return JsonResponse({
            'success': True,
            'dates': sorted_dates,
            'counts': [dates_count[date] for date in sorted_dates]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def donnees_score_emotionnel(request):
    """API pour le score émotionnel"""
    try:
        # Données simulées pour la démo - pourrait être calculé à partir des analyses réelles
        return JsonResponse({
            'success': True,
            'scores': [75, 60, 80, 55, 70]  # Positivité, Stabilité, Intensité, Diversité, Croissance
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def bilan_mensuel(request, annee=None, mois=None):
    """Vue pour afficher les bilans mensuels"""
    try:
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
    
    except Exception as e:
        # Gestion d'erreur pour l'utilisateur
        context = {
            'error': f"Erreur lors du chargement du bilan: {str(e)}"
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





# dashboard/views.py - Mettez à jour la vue analyse_rapide

@login_required
def analyse_rapide(request):
    """Vue pour l'analyse rapide des entrées de journal"""
    try:
        # Récupérer les entrées récentes de l'utilisateur
        entries_recentes = Journal.objects.filter(
            utilisateur=request.user
        ).order_by('-date_creation')[:10]
        
        # Récupérer TOUTES les analyses rapides de l'utilisateur
        analyses_rapides = AnalyseRapide.objects.filter(
            utilisateur=request.user
        ).order_by('-date_creation')
        
        print(f"📊 Analyses rapides trouvées: {analyses_rapides.count()}")  # Debug
        
        context = {
            'entries_recentes': entries_recentes,
            'analyses_rapides': analyses_rapides,
        }
        
        return render(request, 'dashboard/analyse_rapide.html', context)
    
    except Exception as e:
        print(f"❌ Erreur dans analyse_rapide: {e}")  # Debug
        context = {
            'error': f"Erreur lors du chargement: {str(e)}",
            'entries_recentes': [],
            'analyses_rapides': []
        }
        return render(request, 'dashboard/analyse_rapide.html', context)


@login_required
def analyser_texte_rapide(request):
    """API pour analyser rapidement un texte (sans sauvegarde automatique)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texte = data.get('texte', '').strip()
            
            if not texte:
                return JsonResponse({
                    'success': False,
                    'error': "Veuillez fournir un texte à analyser"
                })
            
            print(f"Texte reçu pour analyse profonde: {texte[:100]}...")
            
            # Utiliser le nouvel analyseur PROFOND
            analyseur = AnalyseurRapide()
            resultat = analyseur.analyser_texte(texte)
            
            # NE PAS sauvegarder automatiquement - seulement retourner les résultats
            # L'utilisateur devra cliquer sur "Sauvegarder" manuellement
            
            return JsonResponse(resultat)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': "Données JSON invalides"
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f"Erreur lors de l'analyse: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Méthode non autorisée'
    }, status=405)


@login_required
@require_http_methods(["POST"])
def sauvegarder_analyse_rapide(request):
    """API pour sauvegarder manuellement une analyse rapide"""
    try:
        data = json.loads(request.body)
        texte = data.get('texte', '')
        resultat_analyse = data.get('resultat_analyse', {})
        
        if not texte:
            return JsonResponse({
                'success': False,
                'error': 'Aucun texte fourni'
            })
        
        if not resultat_analyse:
            return JsonResponse({
                'success': False,
                'error': 'Aucun résultat d\'analyse fourni'
            })
        
        print(f"💾 Sauvegarde manuelle pour texte: {texte[:50]}...")
        
        # Sauvegarder dans le modèle AnalyseRapide
        analyse_complete = resultat_analyse.get('analyse_complete', {})
        sentiment_principal = analyse_complete.get('sentiment_principal', {})
        emotions_detectees = analyse_complete.get('emotions_detectees', {})
        themes_psychologiques = analyse_complete.get('themes_psychologiques', {})
        patterns_cognitifs = analyse_complete.get('patterns_cognitifs', {})
        recommandations = analyse_complete.get('recommandations', [])
        
        # Extraire les mots-clés
        mots_cles_data = analyse_complete.get('mots_cles_significatifs', [])
        mots_cles = [mot['mot'] for mot in mots_cles_data] if mots_cles_data else []
        
        # Extraire les thèmes
        themes_detectes = list(themes_psychologiques.keys()) if themes_psychologiques else []
        
        # Créer l'analyse rapide
        analyse_rapide = AnalyseRapide.objects.create(
            utilisateur=request.user,
            texte_original=texte,
            mots_cles=mots_cles,
            ton_general=sentiment_principal.get('ton', 'neutre'),
            themes_detectes=themes_detectes,
            resume_analyse=analyse_complete.get('insights_psychologiques', ['Analyse complétée'])[0] if analyse_complete.get('insights_psychologiques') else 'Analyse complétée',
            score_sentiment=sentiment_principal.get('score', 0),
            confiance_analyse=sentiment_principal.get('confiance', 0),
            emotions_detectees=emotions_detectees,
            patterns_cognitifs=patterns_cognitifs,
            themes_psychologiques=themes_psychologiques,
            recommandations=recommandations,
            date_analyse=datetime.now()
        )
        
        print(f"✅ Analyse sauvegardée - ID: {analyse_rapide.id}")
        
        return JsonResponse({
            'success': True,
            'analysis_id': str(analyse_rapide.id),
            'message': 'Analyse sauvegardée avec succès'
        })
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la sauvegarde: {str(e)}'
        }, status=500)


# Version simplifiée - à utiliser si les champs score_sentiment et confiance_analyse n'existent pas

# dashboard/views.py - Version corrigée



# dashboard/views.py - Version corrigée sans sauvegarde automatique

@login_required
def analyser_texte_rapide(request):
    """API pour analyser rapidement un texte (SANS sauvegarde automatique)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texte = data.get('texte', '').strip()
            
            if not texte:
                return JsonResponse({
                    'success': False,
                    'error': "Veuillez fournir un texte à analyser"
                })
            
            print(f"Texte reçu pour analyse profonde: {texte[:100]}...")
            
            # Utiliser le nouvel analyseur PROFOND
            analyseur = AnalyseurRapide()
            resultat = analyseur.analyser_texte(texte)
            
            # IMPORTANT: NE PAS sauvegarder automatiquement
            # Seulement retourner les résultats pour affichage
            # L'utilisateur devra cliquer sur "Sauvegarder" manuellement
            
            print(f"✅ Analyse terminée - Résultats retournés (sans sauvegarde automatique)")
            
            return JsonResponse(resultat)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': "Données JSON invalides"
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f"Erreur lors de l'analyse: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Méthode non autorisée'
    }, status=405)


@login_required
@require_http_methods(["POST"])
def sauvegarder_analyse_rapide(request):
    """API pour sauvegarder manuellement une analyse rapide"""
    try:
        data = json.loads(request.body)
        texte = data.get('texte', '')
        resultat_analyse = data.get('resultat_analyse', {})
        
        if not texte:
            return JsonResponse({
                'success': False,
                'error': 'Aucun texte fourni'
            })
        
        if not resultat_analyse:
            return JsonResponse({
                'success': False,
                'error': 'Aucun résultat d\'analyse fourni'
            })
        
        print(f"💾 Sauvegarde MANUELLE demandée pour texte: {texte[:50]}...")
        
        # Sauvegarder dans le modèle AnalyseRapide
        analyse_complete = resultat_analyse.get('analyse_complete', {})
        sentiment_principal = analyse_complete.get('sentiment_principal', {})
        emotions_detectees = analyse_complete.get('emotions_detectees', {})
        themes_psychologiques = analyse_complete.get('themes_psychologiques', {})
        patterns_cognitifs = analyse_complete.get('patterns_cognitifs', {})
        recommandations = analyse_complete.get('recommandations', [])
        
        # Extraire les mots-clés
        mots_cles_data = analyse_complete.get('mots_cles_significatifs', [])
        mots_cles = [mot['mot'] for mot in mots_cles_data] if mots_cles_data else []
        
        # Extraire les thèmes
        themes_detectes = list(themes_psychologiques.keys()) if themes_psychologiques else []
        
        # Créer l'analyse rapide
        analyse_rapide = AnalyseRapide.objects.create(
            utilisateur=request.user,
            texte_original=texte,
            mots_cles=mots_cles,
            ton_general=sentiment_principal.get('ton', 'neutre'),
            themes_detectes=themes_detectes,
            resume_analyse=analyse_complete.get('insights_psychologiques', ['Analyse complétée'])[0] if analyse_complete.get('insights_psychologiques') else 'Analyse complétée',
            score_sentiment=sentiment_principal.get('score', 0),
            confiance_analyse=sentiment_principal.get('confiance', 0),
            emotions_detectees=emotions_detectees,
            patterns_cognitifs=patterns_cognitifs,
            themes_psychologiques=themes_psychologiques,
            recommandations=recommandations,
            date_analyse=datetime.now()
        )
        
        print(f"✅ Analyse sauvegardée MANUELLEMENT - ID: {analyse_rapide.id}")
        
        return JsonResponse({
            'success': True,
            'analysis_id': str(analyse_rapide.id),
            'message': 'Analyse sauvegardée avec succès'
        })
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde MANUELLE: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la sauvegarde: {str(e)}'
        }, status=500)





# dashboard/views.py - Ajoutez cette fonction

@login_required
def analyse_details(request, analysis_id):
    """API pour récupérer les détails d'une analyse rapide"""
    try:
        # Récupérer l'analyse
        analyse = AnalyseRapide.objects.get(
            id=analysis_id,
            utilisateur=request.user  # Sécurité: vérifier que l'analyse appartient à l'utilisateur
        )
        
        # Préparer les données pour le JSON
        donnees_analyse = {
            'id': str(analyse.id),
            'texte_original': analyse.texte_original,
            'ton_general': analyse.ton_general,
            'score_sentiment': analyse.score_sentiment,
            'confiance_analyse': analyse.confiance_analyse,
            'mots_cles': analyse.mots_cles,
            'themes_detectes': analyse.themes_detectes,
            'emotions_detectees': analyse.emotions_detectees,
            'patterns_cognitifs': analyse.patterns_cognitifs,
            'themes_psychologiques': analyse.themes_psychologiques,
            'recommandations': analyse.recommandations,
            'resume_analyse': analyse.resume_analyse,
            'date_creation': analyse.date_creation.isoformat(),
            'date_analyse': analyse.date_analyse.isoformat(),
        }
        
        return JsonResponse({
            'success': True,
            'analyse': donnees_analyse
        })
        
    except AnalyseRapide.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Analyse non trouvée'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la récupération: {str(e)}'
        }, status=500)
