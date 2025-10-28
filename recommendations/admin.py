from django.contrib import admin
from .models import Recommandation, Objectif

@admin.register(Recommandation)
class RecommandationAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type', 'statut', 'date_emission']
    list_filter = ['type', 'statut', 'date_emission']
    search_fields = ['utilisateur__username', 'utilisateur__email', 'contenu']
    readonly_fields = ['id', 'date_emission']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'utilisateur', 'statistique', 'date_emission')
        }),
        ('Recommandation', {
            'fields': ('type', 'contenu', 'statut')
        }),

    )


@admin.register(Objectif)
class ObjectifAdmin(admin.ModelAdmin):
    list_display = ['nom', 'utilisateur', 'progres', 'date_debut', 'date_fin', 'est_termine']
    list_filter = ['date_debut', 'date_fin', 'date_creation']
    search_fields = ['nom', 'description', 'utilisateur__username', 'utilisateur__email']
    readonly_fields = ['id', 'date_creation', 'date_mise_a_jour']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'utilisateur', 'date_creation', 'date_mise_a_jour')
        }),
        ('Détails de l\'objectif', {
            'fields': ('nom', 'description', 'progres', 'date_debut', 'date_fin')
        }),
    )
    
    def est_termine(self, obj):
        return "✓" if obj.est_termine else "✗"
    est_termine.short_description = "Terminé"
