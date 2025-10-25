from django.contrib import admin
from .models import RapportPDF, AssistantIA, SuggestionConnexion

@admin.register(RapportPDF)
class RapportPDFAdmin(admin.ModelAdmin):
    list_display = ['statistique', 'mois', 'date_generation']
    list_filter = ['date_generation', 'mois']
    search_fields = ['statistique__utilisateur__username', 'mois']
    readonly_fields = ['id', 'date_generation']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'statistique', 'mois', 'date_generation')
        }),
        ('Contenu', {
            'fields': ('contenu_pdf',)
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
