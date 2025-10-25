from django.contrib import admin
from .models import Statistique

@admin.register(Statistique)
class StatistiqueAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'periode', 'frequence_ecriture', 'score_humeur', 'date_creation']
    list_filter = ['date_creation', 'periode']
    search_fields = ['utilisateur__username', 'utilisateur__email', 'periode', 'bilan_mensuel']
    readonly_fields = ['id', 'date_creation', 'date_mise_a_jour']
    filter_horizontal = ['analyses_liees']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'utilisateur', 'periode', 'date_creation', 'date_mise_a_jour')
        }),
        ('Statistiques', {
            'fields': ('frequence_ecriture', 'score_humeur', 'themes_dominants', 'bilan_mensuel')
        }),
        ('Relations', {
            'fields': ('analyses_liees',)
        }),
    )
