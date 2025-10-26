from django.db import models
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class RapportPDF(models.Model):
    """Enhanced model for PDF Generation System with multiple templates and branding"""
    
    FORMAT_RAPPORT_CHOICES = [
        ('complet', '📊 Rapport Complet'),
        ('resume', '📝 Rapport Résumé'),
        ('statistiques', '📈 Rapport Statistiques'),
        ('emotionnel', '😊 Rapport Émotionnel'),
        ('hebdomadaire', '📅 Rapport Hebdomadaire'),
        ('personnalise', '🎨 Rapport Personnalisé'),
    ]
    
    TEMPLATE_CHOICES = [
        ('moderne', 'Moderne - Design contemporain'),
        ('classique', 'Classique - Style professionnel'),
        ('minimaliste', 'Minimaliste - Épuré et simple'),
        ('coloré', 'Coloré - Vibrant et énergique'),
        ('sombre', 'Sombre - Mode nuit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rapports_pdf',
        verbose_name="Utilisateur"
    )
    statistique = models.ForeignKey(
        'dashboard.Statistique',
        on_delete=models.CASCADE,
        related_name='rapport_pdf',
        verbose_name="Statistique"
    )
    
    # Détails du rapport
    titre = models.CharField(max_length=200, verbose_name="Titre du rapport", default="Rapport Mensuel")
    mois = models.CharField(max_length=50, verbose_name="Mois")
    description = models.TextField(blank=True, verbose_name="Description du rapport")
    
    # Multiple Report Templates & Customizable Content
    format_rapport = models.CharField(
        max_length=20,
        choices=FORMAT_RAPPORT_CHOICES,
        default='complet',
        verbose_name="Format du rapport"
    )
    template_rapport = models.CharField(
        max_length=20,
        choices=TEMPLATE_CHOICES,
        default='moderne',
        verbose_name="Template du rapport"
    )
    
    # Branded Styling Options
    couleur_principale = models.CharField(
        max_length=7, 
        default='#3498db', 
        verbose_name="Couleur principale",
        help_text="Couleur en hexadécimal (#3498db)"
    )
    couleur_secondaire = models.CharField(
        max_length=7, 
        default='#2c3e50', 
        verbose_name="Couleur secondaire"
    )
    inclure_logo = models.BooleanField(default=True, verbose_name="Inclure le logo")
    police_rapport = models.CharField(
        max_length=50,
        default='Helvetica',
        verbose_name="Police de caractères",
        choices=[
            ('Helvetica', 'Helvetica - Moderne'),
            ('Times-Roman', 'Times - Classique'),
            ('Courier', 'Courier - Technique'),
        ]
    )
    
    # Customizable Content Sections
    sections_personnalisees = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Sections personnalisées",
        help_text="Configuration des sections à inclure"
    )
    
    # Content Options
    inclure_statistiques = models.BooleanField(default=True, verbose_name="Inclure les statistiques")
    inclure_graphiques = models.BooleanField(default=True, verbose_name="Inclure les graphiques")
    inclure_analyse_ia = models.BooleanField(default=True, verbose_name="Inclure l'analyse IA")
    inclure_journaux = models.BooleanField(default=False, verbose_name="Inclure les entrées de journal")
    inclure_objectifs = models.BooleanField(default=True, verbose_name="Inclure les objectifs")
    inclure_recommandations = models.BooleanField(default=True, verbose_name="Inclure les recommandations")
    
    # File and Status
    contenu_pdf = models.FileField(
        upload_to='rapports_pdf/%Y/%m/', 
        verbose_name="Fichier PDF", 
        null=True, 
        blank=True
    )
    statut = models.CharField(
        max_length=20,
        choices=[
            ('brouillon', 'Brouillon'),
            ('en_cours', 'Génération en cours'),
            ('termine', 'Terminé'),
            ('erreur', 'Erreur')
        ],
        default='brouillon',
        verbose_name="Statut"
    )
    
    # Sharing and Metadata
    partage_autorise = models.BooleanField(default=False, verbose_name="Partage autorisé")
    mot_de_passe = models.CharField(max_length=100, blank=True, verbose_name="Mot de passe PDF")
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    def __str__(self):
        return f"{self.titre} - {self.mois} - {self.utilisateur.username}"
    
    def generer_nom_fichier(self):
        return f"rapport_{self.mois.lower().replace(' ', '_')}_{self.id}.pdf"
    
    def get_sections_actives(self):
        """Retourne les sections activées pour ce rapport"""
        sections = {}
        if self.sections_personnalisees:
            return self.sections_personnalisees
        
        # Sections par défaut basées sur les paramètres
        sections = {
            'resume_executif': True,
            'statistiques_cles': self.inclure_statistiques,
            'analyse_humeur': self.inclure_analyse_ia,
            'graphiques_evolution': self.inclure_graphiques,
            'themes_dominants': True,
            'objectifs_progres': self.inclure_objectifs,
            'recommandations': self.inclure_recommandations,
            'extraits_journal': self.inclure_journaux,
        }
        return sections
    
    def get_configuration_styling(self):
        """Retourne la configuration de style pour la génération PDF"""
        return {
            'couleur_principale': self.couleur_principale,
            'couleur_secondaire': self.couleur_secondaire,
            'template': self.template_rapport,
            'police': self.police_rapport,
            'inclure_logo': self.inclure_logo,
        }
    
    def save(self, *args, **kwargs):
        """Override save to handle file naming"""
        if not self.contenu_pdf and self.statut == 'termine':
            # Set filename when status changes to 'termine'
            filename = self.generer_nom_fichier()
            # This will be handled when we actually save the file
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to remove the actual PDF file from storage"""
        try:
            # Delete the PDF file from storage
            if self.contenu_pdf:
                storage, path = self.contenu_pdf.storage, self.contenu_pdf.path
                storage.delete(path)
                logger.info(f"PDF file deleted: {path}")
        except Exception as e:
            logger.error(f"Error deleting PDF file: {str(e)}")
        
        # Delete associated generation history
        self.historique_generations.all().delete()
        
        # Call parent delete method
        super().delete(*args, **kwargs)
    
    @property
    def est_pret(self):
        return self.statut == 'termine' and self.contenu_pdf
    
    @property
    def taille_fichier(self):
        if self.contenu_pdf and self.contenu_pdf.size:
            return self.contenu_pdf.size
        return 0
    
    class Meta:
        verbose_name = "Rapport PDF"
        verbose_name_plural = "Rapports PDF"
        ordering = ['-date_generation']
        indexes = [
            models.Index(fields=['utilisateur', 'date_generation']),
            models.Index(fields=['statut']),
        ]


class ModeleRapport(models.Model):
    """Modèles prédéfinis pour les rapports PDF"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, verbose_name="Nom du modèle")
    description = models.TextField(blank=True, verbose_name="Description")
    format_rapport = models.CharField(
        max_length=20,
        choices=RapportPDF.FORMAT_RAPPORT_CHOICES,
        verbose_name="Format"
    )
    template_rapport = models.CharField(
        max_length=20,
        choices=RapportPDF.TEMPLATE_CHOICES,
        verbose_name="Template"
    )
    
    # Configuration par défaut
    configuration = models.JSONField(
        default=dict,
        verbose_name="Configuration du modèle",
        help_text="Paramètres par défaut pour ce modèle"
    )
    
    public = models.BooleanField(default=True, verbose_name="Modèle public")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    def __str__(self):
        return f"{self.nom} ({self.get_format_rapport_display()})"
    
    class Meta:
        verbose_name = "Modèle de rapport"
        verbose_name_plural = "Modèles de rapports"


class HistoriqueGeneration(models.Model):
    """Historique des générations de rapports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rapport = models.ForeignKey(
        RapportPDF,
        on_delete=models.CASCADE,
        related_name='historique_generations',
        verbose_name="Rapport"
    )
    date_debut = models.DateTimeField(auto_now_add=True, verbose_name="Date de début")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    statut = models.CharField(
        max_length=20,
        choices=[
            ('debute', 'Débuté'),
            ('reussi', 'Réussi'),
            ('echoue', 'Échoué')
        ],
        verbose_name="Statut"
    )
    message_erreur = models.TextField(blank=True, verbose_name="Message d'erreur")
    duree_generation = models.FloatField(null=True, blank=True, verbose_name="Durée (secondes)")
    
    def __str__(self):
        return f"Génération {self.rapport.titre} - {self.statut}"
    
    def save(self, *args, **kwargs):
        if self.date_fin and self.date_debut:
            self.duree_generation = (self.date_fin - self.date_debut).total_seconds()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Historique de génération"
        verbose_name_plural = "Historiques de génération"
        ordering = ['-date_debut']


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
