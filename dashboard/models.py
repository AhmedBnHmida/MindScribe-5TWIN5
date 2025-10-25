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
