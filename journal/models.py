from django.db import models
from django.conf import settings
import uuid

class Journal(models.Model):
    """Model pour les entrées de journal multimodal"""
    
    TYPE_ENTREE_CHOICES = [
        ('texte', 'Texte'),
        ('audio', 'Audio'),
        ('image', 'Image'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journaux',
        verbose_name="Utilisateur"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    categorie = models.CharField(max_length=100, blank=True, verbose_name="Catégorie")
    
    # Contenu multimodal
    contenu_texte = models.TextField(blank=True, verbose_name="Contenu texte")
    audio = models.FileField(upload_to='journal_audio/', blank=True, null=True, verbose_name="Fichier audio")
    image = models.ImageField(upload_to='journal_images/', blank=True, null=True, verbose_name="Image")
    
    type_entree = models.CharField(
        max_length=10,
        choices=TYPE_ENTREE_CHOICES,
        default='texte',
        verbose_name="Type d'entrée"
    )
    
    def __str__(self):
        return f"Journal {self.utilisateur.username} - {self.date_creation.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Journal"
        verbose_name_plural = "Journaux"
        ordering = ['-date_creation']
