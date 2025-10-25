from django.db import models
import uuid

class AnalyseIA(models.Model):
    """Model pour l'analyse IA des entrées de journal"""
    
    TON_GENERAL_CHOICES = [
        ('positif', 'Positif'),
        ('neutre', 'Neutre'),
        ('negatif', 'Négatif'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal = models.OneToOneField(
        'journal.Journal',
        on_delete=models.CASCADE,
        related_name='analyse',
        verbose_name="Journal"
    )
    
    # Résultats de l'analyse
    mots_cles = models.JSONField(default=list, blank=True, verbose_name="Mots-clés")
    ton_general = models.CharField(
        max_length=10,
        choices=TON_GENERAL_CHOICES,
        default='neutre',
        verbose_name="Ton général"
    )
    themes_detectes = models.JSONField(default=list, blank=True, verbose_name="Thèmes détectés")
    resume_journee = models.TextField(blank=True, verbose_name="Résumé de la journée")
    
    # Métadonnées
    date_analyse = models.DateTimeField(auto_now_add=True, verbose_name="Date d'analyse")
    
    def __str__(self):
        return f"Analyse {self.journal.utilisateur.username} - {self.journal.date_creation.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name = "Analyse IA"
        verbose_name_plural = "Analyses IA"
        ordering = ['-date_analyse']
