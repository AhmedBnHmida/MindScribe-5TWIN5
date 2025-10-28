from django.db import models
from django.conf import settings
import uuid

class Statistique(models.Model):
    """Model pour les statistiques et le suivi de l'utilisateur"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='statistiques',
        verbose_name="Utilisateur"
    )
    
    # Période de suivi
    periode = models.CharField(max_length=50, verbose_name="Période")
    
    # Statistiques calculées
    frequence_ecriture = models.IntegerField(default=0, verbose_name="Fréquence d'écriture")
    score_humeur = models.FloatField(default=0.0, verbose_name="Score d'humeur")
    themes_dominants = models.JSONField(default=list, blank=True, verbose_name="Thèmes dominants")
    bilan_mensuel = models.TextField(blank=True, verbose_name="Bilan mensuel")
    
    # Relation avec les analyses
    analyses_liees = models.ManyToManyField(
        'analysis.AnalyseIA',
        related_name='statistiques',
        blank=True,
        verbose_name="Analyses liées"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    def __str__(self):
        return f"Statistique {self.utilisateur.username} - {self.periode}"
    
    class Meta:
        verbose_name = "Statistique"
        verbose_name_plural = "Statistiques"
        ordering = ['-date_creation']

class AnalyseRapide(models.Model):
    """Modèle pour stocker les analyses rapides générées par l'IA"""
    
    TON_GENERAL_CHOICES = [
        ('positif', 'Positif'),
        ('neutre', 'Neutre'),
        ('negatif', 'Négatif'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses_rapides',
        verbose_name="Utilisateur"
    )
    
    # Texte analysé
    texte_original = models.TextField(verbose_name="Texte original")
    
    # Résultats de l'analyse
    mots_cles = models.JSONField(default=list, verbose_name="Mots-clés détectés")
    ton_general = models.CharField(
        max_length=10,
        choices=TON_GENERAL_CHOICES,
        default='neutre',
        verbose_name="Ton général"
    )
    themes_detectes = models.JSONField(default=list, verbose_name="Thèmes détectés")
    resume_analyse = models.TextField(verbose_name="Résumé de l'analyse")
    
    # Métriques d'analyse profonde
    score_sentiment = models.FloatField(default=0.0, verbose_name="Score de sentiment")
    confiance_analyse = models.FloatField(default=0.0, verbose_name="Confiance de l'analyse")
    emotions_detectees = models.JSONField(default=dict, verbose_name="Émotions détectées")
    patterns_cognitifs = models.JSONField(default=dict, verbose_name="Patterns cognitifs")
    themes_psychologiques = models.JSONField(default=dict, verbose_name="Thèmes psychologiques")
    recommandations = models.JSONField(default=list, verbose_name="Recommandations")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_analyse = models.DateTimeField(auto_now=True, verbose_name="Date d'analyse")
    
    def __str__(self):
        return f"Analyse Rapide {self.utilisateur.username} - {self.date_creation.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def texte_tronque(self):
        """Retourne le texte tronqué pour l'affichage"""
        return self.texte_original[:100] + "..." if len(self.texte_original) > 100 else self.texte_original
    
    @property
    def nombre_mots_cles(self):
        """Retourne le nombre de mots-clés détectés"""
        return len(self.mots_cles)
    
    @property
    def nombre_themes(self):
        """Retourne le nombre de thèmes détectés"""
        return len(self.themes_detectes)
    
    class Meta:
        verbose_name = "Analyse Rapide"
        verbose_name_plural = "Analyses Rapides"
        ordering = ['-date_creation']

class BilanMensuel(models.Model):
    """Modèle pour stocker les bilans mensuels générés par l'IA"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('genere', 'Généré'),
        ('erreur', 'Erreur'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bilans_mensuels',
        verbose_name="Utilisateur"
    )
    
    # Lien avec la statistique existante
    statistique = models.OneToOneField(
        'dashboard.Statistique',
        on_delete=models.CASCADE,
        related_name='bilan_ia',
        verbose_name="Statistique associée"
    )
    
    # Contenu généré par l'IA
    titre = models.CharField(max_length=200, verbose_name="Titre du bilan")
    resume = models.TextField(verbose_name="Résumé exécutif")
    points_cles = models.JSONField(default=list, verbose_name="Points clés")
    tendances = models.JSONField(default=list, verbose_name="Tendances détectées")
    recommandations = models.JSONField(default=list, verbose_name="Recommandations")
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_generation = models.DateTimeField(null=True, blank=True, verbose_name="Date de génération")
    
    def __str__(self):
        return f"Bilan {self.statistique.periode} - {self.utilisateur.username}"
    
    @property
    def periode(self):
        return self.statistique.periode
    
    @property
    def humeur_moyenne(self):
        return self.statistique.score_humeur
    
    @property
    def frequence_ecriture(self):
        return self.statistique.frequence_ecriture
    
    @property
    def themes_dominants(self):
        return self.statistique.themes_dominants
    
    class Meta:
        verbose_name = "Bilan Mensuel IA"
        verbose_name_plural = "Bilans Mensuels IA"
        ordering = ['-date_creation']