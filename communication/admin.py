from django.contrib import admin
from .models import RapportPDF, ModeleRapport, HistoriqueGeneration, AssistantIA, SuggestionConnexion

@admin.register(RapportPDF)
class RapportPDFAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'utilisateur', 'mois', 'format_rapport', 
        'template_rapport', 'statut', 'date_generation'
    ]
    list_filter = [
        'format_rapport', 'template_rapport', 'statut', 
        'date_generation', 'inclure_statistiques', 'inclure_graphiques'
    ]
    search_fields = [
        'titre', 'utilisateur__username', 'mois', 
        'statistique__periode'
    ]
    readonly_fields = ['id', 'date_generation', 'date_mise_a_jour']
    list_editable = ['statut']
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'id', 'utilisateur', 'statistique', 'titre', 
                'mois', 'description', 'format_rapport'
            )
        }),
        ('Personnalisation du contenu', {
            'fields': (
                'template_rapport',
                'inclure_statistiques', 'inclure_graphiques',
                'inclure_analyse_ia', 'inclure_journaux',
                'inclure_objectifs', 'inclure_recommandations',
                'sections_personnalisees'
            )
        }),
        ('Style et apparence', {
            'fields': (
                'couleur_principale', 'couleur_secondaire',
                'police_rapport', 'inclure_logo'
            )
        }),
        ('Fichier et statut', {
            'fields': (
                'contenu_pdf', 'statut', 'partage_autorise', 'mot_de_passe'
            )
        }),
        ('Métadonnées', {
            'fields': ('date_generation', 'date_mise_a_jour')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.statut == 'termine':
            return self.readonly_fields + ['format_rapport', 'template_rapport']
        return self.readonly_fields


@admin.register(ModeleRapport)
class ModeleRapportAdmin(admin.ModelAdmin):
    list_display = ['nom', 'format_rapport', 'template_rapport', 'public', 'date_creation']
    list_filter = ['format_rapport', 'template_rapport', 'public']
    search_fields = ['nom', 'description']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'format_rapport', 'template_rapport', 'public')
        }),
        ('Configuration par défaut', {
            'fields': ('configuration',)
        }),
    )


@admin.register(HistoriqueGeneration)
class HistoriqueGenerationAdmin(admin.ModelAdmin):
    list_display = ['rapport', 'date_debut', 'date_fin', 'statut', 'duree_generation']
    list_filter = ['statut', 'date_debut']
    search_fields = ['rapport__titre', 'message_erreur']
    readonly_fields = ['id', 'date_debut', 'duree_generation']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('rapport', 'statut')
        }),
        ('Détails de génération', {
            'fields': ('date_debut', 'date_fin', 'duree_generation', 'message_erreur')
        }),
    )


@admin.register(AssistantIA)
class AssistantIAAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'journal', 'date_interaction']
    list_filter = ['date_interaction']
    search_fields = ['utilisateur__username', 'message_utilisateur', 'reponse_ia']
    readonly_fields = ['id', 'date_interaction']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'utilisateur', 'journal', 'date_interaction')
        }),
        ('Conversation', {
            'fields': ('message_utilisateur', 'reponse_ia')
        }),
    )


@admin.register(SuggestionConnexion)
class SuggestionConnexionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur_source', 'utilisateur_cible', 'type_suggestion', 'score_similarite', 'statut', 'date_suggestion']
    list_filter = ['type_suggestion', 'statut', 'date_suggestion']
    search_fields = ['utilisateur_source__username', 'utilisateur_cible__username']
    readonly_fields = ['id', 'date_suggestion']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'date_suggestion')
        }),
        ('Utilisateurs', {
            'fields': ('utilisateur_source', 'utilisateur_cible')
        }),
        ('Détails de la suggestion', {
            'fields': ('type_suggestion', 'score_similarite', 'statut')
        }),
    )
