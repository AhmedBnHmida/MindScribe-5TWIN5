from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('admin', 'Administrateur'),
    ]
    
    # Champs de base requis
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    
    # Rôle utilisateur
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user', 
        verbose_name="Rôle"
    )
    
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