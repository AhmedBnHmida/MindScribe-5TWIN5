from django.db import models
from django.conf import settings
import uuid

class RapportPDF(models.Model):
    """Model pour les rapports PDF mensuels"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    statistique = models.OneToOneField(
        'dashboard.Statistique',
        on_delete=models.CASCADE,
        related_name='rapport_pdf',
        verbose_name="Statistique"
    )
    
    # Détails du rapport
    mois = models.CharField(max_length=50, verbose_name="Mois")  # Ex: "Janvier 2024"
    contenu_pdf = models.FileField(upload_to='rapports_pdf/', verbose_name="Fichier PDF")
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    
    def __str__(self):
        return f"Rapport PDF {self.mois} - {self.statistique.utilisateur.username}"
    
    class Meta:
        verbose_name = "Rapport PDF"
        verbose_name_plural = "Rapports PDF"
        ordering = ['-date_generation']


class AssistantIA(models.Model):
    """Model pour les interactions avec l'assistant IA"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_ia',
        verbose_name="Utilisateur"
    )
    journal = models.ForeignKey(
        'journal.Journal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations_ia',
        verbose_name="Journal de référence"
    )
    
    # Conversation
    message_utilisateur = models.TextField(verbose_name="Message utilisateur")
    reponse_ia = models.TextField(verbose_name="Réponse IA")
    date_interaction = models.DateTimeField(auto_now_add=True, verbose_name="Date d'interaction")
    
    def __str__(self):
        return f"Conversation {self.utilisateur.username} - {self.date_interaction.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Assistant IA"
        verbose_name_plural = "Assistants IA"
        ordering = ['-date_interaction']


class SuggestionConnexion(models.Model):
    """Model pour les suggestions de connexion entre utilisateurs"""
    
    TYPE_SUGGESTION_CHOICES = [
        ('objectif_similaire', 'Objectif similaire'),
        ('humeur_proche', 'Humeur proche'),
        ('interet_commun', 'Intérêt commun'),
    ]
    
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('ignoree', 'Ignorée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur_source = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='suggestions_envoyees',
        verbose_name="Utilisateur source"
    )
    utilisateur_cible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='suggestions_recues',
        verbose_name="Utilisateur cible"
    )
    
    # Détails de la suggestion
    score_similarite = models.FloatField(verbose_name="Score de similarité")
    type_suggestion = models.CharField(
        max_length=20,
        choices=TYPE_SUGGESTION_CHOICES,
        verbose_name="Type de suggestion"
    )
    date_suggestion = models.DateTimeField(auto_now_add=True, verbose_name="Date de suggestion")
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='proposee',
        verbose_name="Statut"
    )
    
    def __str__(self):
        return f"Suggestion {self.utilisateur_source.username} → {self.utilisateur_cible.username}"
    
    class Meta:
        verbose_name = "Suggestion de connexion"
        verbose_name_plural = "Suggestions de connexion"
        ordering = ['-date_suggestion']
        unique_together = ['utilisateur_source', 'utilisateur_cible']
