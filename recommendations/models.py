from django.db import models
from django.conf import settings
import uuid

class Recommandation(models.Model):
    """Model pour les recommandations personnalisées"""
    
    TYPE_CHOICES = [
        ('bien_etre', 'Bien-être'),
        ('productivite', 'Productivité'),
        ('sommeil', 'Sommeil'),
        ('nutrition', 'Nutrition'),
    ]
    
    STATUT_CHOICES = [
        ('nouvelle', 'Nouvelle'),
        ('suivie', 'Suivie'),
        ('ignoree', 'Ignorée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommandations',
        verbose_name="Utilisateur"
    )
    statistique = models.ForeignKey(
        'dashboard.Statistique',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommandations',
        verbose_name="Statistique"
    )
    
    # Contenu de la recommandation
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type"
    )
    contenu = models.TextField(verbose_name="Contenu")
    date_emission = models.DateTimeField(auto_now_add=True, verbose_name="Date d'émission")
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='nouvelle',
        verbose_name="Statut"
    )
    
    # Feedback system
    utile = models.BooleanField(null=True, blank=True, verbose_name="Utile")
    feedback_note = models.IntegerField(null=True, blank=True, verbose_name="Note (1-5)")
    feedback_commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    
    def __str__(self):
        return f"Recommandation {self.type} pour {self.utilisateur.username}"
    
    class Meta:
        verbose_name = "Recommandation"
        verbose_name_plural = "Recommandations"
        ordering = ['-date_emission']


class Objectif(models.Model):
    """Model pour les objectifs personnels de l'utilisateur"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='objectifs',
        verbose_name="Utilisateur"
    )
    
    # Détails de l'objectif
    nom = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    progres = models.FloatField(default=0.0, verbose_name="Progrès (%)")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    def __str__(self):
        return f"{self.nom} - {self.utilisateur.username} ({self.progres}%)"
    
    @property
    def est_termine(self):
        return self.progres >= 100.0
    
    class Meta:
        verbose_name = "Objectif"
        verbose_name_plural = "Objectifs"
        ordering = ['-date_creation']
