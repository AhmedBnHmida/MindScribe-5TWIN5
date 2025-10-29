# dashboard/services.py
from datetime import datetime, timedelta
from collections import Counter
from module2_analysis.models import JournalAnalysis
from journal.models import Journal
from .models import BilanMensuel, Statistique
import json
import random

class ServiceBilanIA:
    """Service pour générer automatiquement les bilans mensuels par IA"""
    
    @staticmethod
    def generer_bilan_mensuel(utilisateur, mois, annee):
        """Génère un bilan mensuel automatique pour un utilisateur"""
        
        periode = f"{mois:02d}/{annee}"
        
        # Récupère ou crée la statistique
        statistique, created = Statistique.objects.get_or_create(
            utilisateur=utilisateur,
            periode=periode,
            defaults=ServiceBilanIA._calculer_statistiques(utilisateur, mois, annee)
        )
        
        if not created:
            # Met à jour les statistiques existantes
            nouvelles_stats = ServiceBilanIA._calculer_statistiques(utilisateur, mois, annee)
            statistique.frequence_ecriture = nouvelles_stats['frequence_ecriture']
            statistique.score_humeur = nouvelles_stats['score_humeur']
            statistique.themes_dominants = nouvelles_stats['themes_dominants']
            statistique.save()
        
        # Génère le contenu IA basé sur les statistiques
        contenu_ia = ServiceBilanIA._generer_contenu_ia(statistique, mois, annee)
        
        # Crée ou met à jour le bilan IA
        bilan, created = BilanMensuel.objects.get_or_create(
            statistique=statistique,
            defaults={
                'utilisateur': utilisateur,
                'titre': contenu_ia['titre'],
                'resume': contenu_ia['resume'],
                'points_cles': contenu_ia['points_cles'],
                'tendances': contenu_ia['tendances'],
                'recommandations': contenu_ia['recommandations'],
                'statut': 'genere',
                'date_generation': datetime.now()
            }
        )
        
        if not created:
            # Met à jour le bilan existant
            for field, value in contenu_ia.items():
                setattr(bilan, field, value)
            bilan.statut = 'genere'
            bilan.date_generation = datetime.now()
            bilan.save()
        
        return bilan
    
    @staticmethod
    def _calculer_statistiques(utilisateur, mois, annee):
        """Calcule les statistiques pour la période"""
        
        date_debut = datetime(annee, mois, 1)
        if mois == 12:
            date_fin = datetime(annee + 1, 1, 1) - timedelta(days=1)
        else:
            date_fin = datetime(annee, mois + 1, 1) - timedelta(days=1)
        
        # Utilise JournalAnalysis au lieu de AnalyseIA
        analyses = JournalAnalysis.objects.filter(
            user=utilisateur,
            created_at__range=[date_debut, date_fin]
        )
        
        journaux = Journal.objects.filter(
            utilisateur=utilisateur,
            date_creation__range=[date_debut, date_fin]
        )
        
        # Calcule l'humeur moyenne basée sur le sentiment
        scores = []
        for analyse in analyses:
            # Convertir le sentiment en score numérique
            sentiment_map = {
                'positif': 1, 'positive': 1, 'happy': 1, 'joyful': 1,
                'neutre': 0, 'neutral': 0, 'mixed': 0,
                'negatif': -1, 'negative': -1, 'sad': -1, 'angry': -1
            }
            score = sentiment_map.get(analyse.sentiment.lower(), 0)
            scores.append(score)
        
        score_humeur = sum(scores) / len(scores) if scores else 0
        
        # Calcule les thèmes dominants
        tous_themes = []
        for analyse in analyses:
            if analyse.topics:
                tous_themes.extend(analyse.topics)
        
        themes_dominants = [theme for theme, count in Counter(tous_themes).most_common(5)]
        
        return {
            'frequence_ecriture': journaux.count(),
            'score_humeur': score_humeur,
            'themes_dominants': themes_dominants,
        }
    
    @staticmethod
    def _generer_contenu_ia(statistique, mois, annee):
        """Génère le contenu du bilan avec une IA simulée"""
        
        noms_mois = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
        
        mois_nom = noms_mois[mois - 1]
        
        # Détermine le ton général basé sur le score d'humeur
        score = statistique.score_humeur
        if score > 0.3:
            ton_general = "positif"
            adjectifs = ["excellent", "très positif", "enthousiasmant", "constructif"]
        elif score < -0.3:
            ton_general = "challenging"
            adjectifs = ["intense", "riche en apprentissages", "transformateur"]
        else:
            ton_general = "équilibré"
            adjectifs = ["stable", "équilibré", "constant"]
        
        # Génération du contenu
        titre = f"Bilan {mois_nom} {annee} : Un mois {random.choice(adjectifs)}"
        
        resume = ServiceBilanIA._generer_resume(statistique, mois_nom, annee, ton_general)
        points_cles = ServiceBilanIA._generer_points_cles(statistique)
        tendances = ServiceBilanIA._generer_tendances(statistique)
        recommandations = ServiceBilanIA._generer_recommandations(statistique)
        
        return {
            'titre': titre,
            'resume': resume,
            'points_cles': points_cles,
            'tendances': tendances,
            'recommandations': recommandations
        }
    
    @staticmethod
    def _generer_resume(statistique, mois_nom, annee, ton_general):
        """Génère le résumé exécutif"""
        
        templates = {
            'positif': [
                f"Ce {mois_nom} {annee} a été marqué par une énergie très positive. ",
                f"Votre mois de {mois_nom} reflète une belle progression avec {statistique.frequence_ecriture} entrées analysées. ",
                f"Excellente consistency dans votre routine d'écriture ce {mois_nom}. "
            ],
            'equilibre': [
                f"Le mois de {mois_nom} {annee} montre une belle stabilité émotionnelle. ",
                f"Votre équilibre émotionnel ce {mois_nom} est remarquable. ",
                f"{mois_nom} a été un mois de consolidation avec une humeur générale stable. "
            ],
            'challenging': [
                f"Ce {mois_nom} {annee} a présenté certains défis émotionnels. ",
                f"Malgré les difficultés perçues, votre pratique d'écriture est restée constante. ",
                f"Le mois de {mois_nom} a été riche en apprentissages émotionnels. "
            ]
        }
        
        ton = 'positif' if ton_general == 'positif' else 'challenging' if ton_general == 'challenging' else 'equilibre'
        
        base = random.choice(templates[ton])
        
        if statistique.frequence_ecriture > 20:
            base += "Votre fréquence d'écriture est particulièrement impressionnante cette période. "
        elif statistique.frequence_ecriture < 5:
            base += "Une opportunité pour renforcer votre routine d'écriture les prochains mois. "
        
        if statistique.themes_dominants:
            base += f"Les thèmes dominants ({', '.join(statistique.themes_dominants[:3])}) révèlent vos centres d'intérêt principaux."
        
        return base
    
    @staticmethod
    def _generer_points_cles(statistique):
        """Génère les points clés du mois"""
        
        points = []
        
        # Point sur l'humeur
        score = statistique.score_humeur
        if score > 0.5:
            points.append("Humeur générale très positive et énergisante")
        elif score > 0:
            points.append("Humeur globalement positive et constructive")
        elif score < -0.5:
            points.append("Période émotionnellement intense avec des défis")
        else:
            points.append("Équilibre émotionnel stable tout au long du mois")
        
        # Point sur la fréquence
        if statistique.frequence_ecriture >= 15:
            points.append("Excellente régularité dans votre pratique d'écriture")
        elif statistique.frequence_ecriture >= 8:
            points.append("Bonne consistance de votre routine de réflexion")
        else:
            points.append("Espace pour développer une habitude d'écriture plus régulière")
        
        # Point sur les thèmes
        if statistique.themes_dominants:
            points.append(f"Focus sur {', '.join(statistique.themes_dominants[:2])} comme thèmes principaux")
        
        return points
    
    @staticmethod
    def _generer_tendances(statistique):
        """Génère les tendances détectées"""
        
        tendances = []
        
        # Tendances d'humeur
        score = statistique.score_humeur
        if score > 0.3:
            tendances.append("Tendance à l'optimisme et la positivité")
        elif score < -0.3:
            tendances.append("Tendance à la réflexion profonde et l'introspection")
        
        # Tendances thématiques
        if len(statistique.themes_dominants) >= 3:
            tendances.append("Diversité thématique dans vos réflexions")
        else:
            tendances.append("Focus sur quelques thèmes centraux")
        
        return tendances
    
    @staticmethod
    def _generer_recommandations(statistique):
        """Génère les recommandations personnalisées"""
        
        recommandations = []
        
        # Recommandations basées sur l'humeur
        score = statistique.score_humeur
        if score < -0.2:
            recommandations.append("Pratiquez la gratitude quotidienne pour équilibrer votre perspective")
            recommandations.append("Explorez des activités qui vous procurent de la joie")
        elif score > 0.5:
            recommandations.append("Capitalisez sur cette énergie positive pour de nouveaux projets")
        
        # Recommandations basées sur la fréquence
        if statistique.frequence_ecriture < 8:
            recommandations.append("Essayez d'écrire 10 minutes chaque jour pour établir une routine")
            recommandations.append("Utilisez des rappels pour maintenir votre pratique d'écriture")
        else:
            recommandations.append("Continuez cette excellente habitude d'écriture régulière")
        
        # Recommandations basées sur les thèmes
        if statistique.themes_dominants:
            if any(theme in ['travail', 'projets', 'professionnel'] for theme in statistique.themes_dominants):
                recommandations.append("Pensez à équilibrer réflexions professionnelles et personnelles")
        
        # Recommandation générale
        recommandations.append("Relisez vos entrées favorites pour constater votre progression")
        
        return recommandations