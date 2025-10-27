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
    periode = models.CharField(max_length=50, verbose_name="Période")  # Ex: "Janvier 2024", "Semaine 12"
    
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





# Ajoute cette classe à ton fichier models.py existant

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