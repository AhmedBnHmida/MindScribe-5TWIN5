from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    # Choices for various enums
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('admin', 'Administrateur'),
    ]
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    STATUS_PROFESSIONNEL_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('travailleur', 'Travailleur'),
        ('freelance', 'Freelance'),
        ('chomeur', 'Chômeur'),
        ('retraite', 'Retraité'),
        ('autre', 'Autre'),
    ]
    
    HUMEUR_GENERALE_CHOICES = [
        ('heureux', 'Heureux'),
        ('neutre', 'Neutre'),
        ('triste', 'Triste'),
        ('anxieux', 'Anxieux'),
        ('stresse', 'Stressé'),
    ]
    
    QUALITE_SOMMEIL_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('moyen', 'Moyen'),
        ('mauvais', 'Mauvais'),
        ('tres_mauvais', 'Très Mauvais'),
    ]
    
    FREQUENCE_ECRITURE_CHOICES = [
        ('matin', 'Matin'),
        ('midi', 'Midi'),
        ('soir', 'Soir'),
        ('nuit', 'Nuit'),
        ('variable', 'Variable'),
    ]
    
    NIVEAU_ACTIVITE_CHOICES = [
        ('sedentaire', 'Sédentaire'),
        ('leger', 'Léger'),
        ('modere', 'Modéré'),
        ('intense', 'Intense'),
        ('tres_intense', 'Très Intense'),
    ]
    
    HABITUDES_ALIMENTAIRES_CHOICES = [
        ('equilibree', 'Équilibrée'),
        ('vegetarien', 'Végétarien'),
        ('vegan', 'Vegan'),
        ('sans_gluten', 'Sans Gluten'),
        ('variable', 'Variable'),
    ]
    
    # UUID field (keeping Django's default id but adding uuid for API)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    
    # Champs de base requis
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True, verbose_name="Photo de profil")
    
    # Rôle utilisateur
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user', 
        verbose_name="Rôle"
    )
    
    # Informations personnelles
    centres_interet = models.JSONField(default=list, blank=True, verbose_name="Centres d'intérêt")
    preferences_suivi = models.JSONField(default=dict, blank=True, verbose_name="Préférences de suivi")
    langue = models.CharField(max_length=10, default='fr', verbose_name="Langue")
    age = models.IntegerField(null=True, blank=True, verbose_name="Âge")
    adresse = models.JSONField(default=dict, blank=True, verbose_name="Adresse")  # {code_postal, province, etc}
    etat_civil = models.CharField(max_length=50, blank=True, verbose_name="État civil")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, blank=True, verbose_name="Sexe")
    status_professionnel = models.CharField(
        max_length=20, 
        choices=STATUS_PROFESSIONNEL_CHOICES, 
        blank=True, 
        verbose_name="Statut professionnel"
    )
    
    # Traits de personnalité
    casanier = models.BooleanField(default=False, verbose_name="Casanier")
    sociable = models.BooleanField(default=False, verbose_name="Sociable")
    
    # Profession et passions
    profession = models.CharField(max_length=100, blank=True, verbose_name="Profession")
    passions = models.JSONField(default=list, blank=True, verbose_name="Passions")
    objectifs_personnels = models.JSONField(default=list, blank=True, verbose_name="Objectifs personnels")
    
    # Routine et habitudes
    routine_quotidienne = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name="Routine quotidienne"
    )  # {matinale, nocturne, variable, reguliere}
    
    # État mental et bien-être
    humeur_generale = models.CharField(
        max_length=20, 
        choices=HUMEUR_GENERALE_CHOICES, 
        default='neutre', 
        verbose_name="Humeur générale"
    )
    niveau_stress = models.IntegerField(default=5, verbose_name="Niveau de stress (0-10)")
    qualite_sommeil = models.CharField(
        max_length=20, 
        choices=QUALITE_SOMMEIL_CHOICES, 
        default='moyen', 
        verbose_name="Qualité de sommeil"
    )
    
    # Préférences d'écriture
    frequence_ecriture_souhaitee = models.CharField(
        max_length=20, 
        choices=FREQUENCE_ECRITURE_CHOICES, 
        default='variable', 
        verbose_name="Fréquence d'écriture souhaitée"
    )
    moment_prefere_ecriture = models.CharField(
        max_length=20, 
        choices=FREQUENCE_ECRITURE_CHOICES, 
        default='variable', 
        verbose_name="Moment préféré d'écriture"
    )
    
    # Santé et activité physique
    niveau_activite_physique = models.CharField(
        max_length=20, 
        choices=NIVEAU_ACTIVITE_CHOICES, 
        default='sedentaire', 
        verbose_name="Niveau d'activité physique"
    )
    habitudes_alimentaires = models.CharField(
        max_length=20, 
        choices=HABITUDES_ALIMENTAIRES_CHOICES, 
        default='equilibree', 
        verbose_name="Habitudes alimentaires"
    )
    heures_sommeil_par_nuit = models.FloatField(default=7.0, verbose_name="Heures de sommeil par nuit")
    
    def __str__(self):
        return f"{self.username} - {self.email}"
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    def save(self, *args, **kwargs):
        # Si l'utilisateur est superuser, son rôle devient automatiquement admin
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_joined']


class Session(models.Model):
    """Model pour gérer les sessions utilisateur"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        verbose_name="Utilisateur"
    )
    date_connexion = models.DateTimeField(auto_now_add=True, verbose_name="Date de connexion")
    adresse_ip = models.GenericIPAddressField(verbose_name="Adresse IP")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    def __str__(self):
        return f"Session {self.utilisateur.username} - {self.date_connexion}"
    
    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        ordering = ['-date_connexion']