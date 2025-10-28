# dashboard/services/sauvegarde_analyse.py
from datetime import datetime
from ..models import AnalyseRapide

class ServiceSauvegardeAnalyse:
    """Service pour sauvegarder les analyses rapides dans la base de données"""
    
    @staticmethod
    def sauvegarder_analyse_rapide(utilisateur, texte, resultat_analyse):
        """Sauvegarde une analyse rapide dans la base de données"""
        
        # Extrait les données de l'analyse
        analyse_complete = resultat_analyse.get('analyse_complete', {})
        
        # Crée et sauvegarde l'analyse rapide
        analyse_rapide = AnalyseRapide.objects.create(
            utilisateur=utilisateur,
            texte_original=texte,
            mots_cles=resultat_analyse.get('mots_cles', []),
            ton_general=resultat_analyse.get('ton_general', 'neutre'),
            themes_detectes=resultat_analyse.get('themes', []),
            resume_analyse=resultat_analyse.get('resume', ''),
            score_sentiment=analyse_complete.get('sentiment_principal', {}).get('score', 0.0),
            confiance_analyse=analyse_complete.get('sentiment_principal', {}).get('confiance', 0.0),
            emotions_detectees=analyse_complete.get('emotions_detectees', {}),
            patterns_cognitifs=analyse_complete.get('patterns_cognitifs', {}),
            themes_psychologiques=analyse_complete.get('themes_psychologiques', {}),
            recommandations=analyse_complete.get('recommandations', [])
        )
        
        return analyse_rapide
    
    @staticmethod
    def get_analyses_rapides_utilisateur(utilisateur, limit=20):
        """Récupère les analyses rapides d'un utilisateur"""
        return AnalyseRapide.objects.filter(
            utilisateur=utilisateur
        ).order_by('-date_creation')[:limit]
    
    @staticmethod
    def get_analyse_rapide_par_id(utilisateur, analyse_id):
        """Récupère une analyse rapide spécifique par ID"""
        try:
            return AnalyseRapide.objects.get(
                id=analyse_id,
                utilisateur=utilisateur
            )
        except AnalyseRapide.DoesNotExist:
            return None
    
    @staticmethod
    def get_statistiques_analyses_rapides(utilisateur):
        """Récupère les statistiques des analyses rapides"""
        analyses = AnalyseRapide.objects.filter(utilisateur=utilisateur)
        
        total_analyses = analyses.count()
        
        # Compte par ton général
        tons = list(analyses.values_list('ton_general', flat=True))
        from collections import Counter
        ton_counts = Counter(tons)
        
        # Dernière analyse
        derniere_analyse = analyses.first()
        
        return {
            'total_analyses': total_analyses,
            'repartition_tons': dict(ton_counts),
            'derniere_analyse_date': derniere_analyse.date_creation if derniere_analyse else None,
            'moyenne_confiance': analyses.aggregate(models.Avg('confiance_analyse'))['confiance_analyse__avg'] or 0
        }