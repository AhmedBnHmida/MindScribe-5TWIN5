from django.contrib import admin
from .models import AnalyseIA

@admin.register(AnalyseIA)
class AnalyseIAAdmin(admin.ModelAdmin):
    list_display = ['journal', 'ton_general', 'date_analyse']
    list_filter = ['ton_general', 'date_analyse']
    search_fields = ['journal__utilisateur__username', 'resume_journee', 'themes_detectes']
    readonly_fields = ['id', 'date_analyse']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'journal', 'date_analyse')
        }),
        ('Résultats d\'analyse', {
            'fields': ('ton_general', 'mots_cles', 'themes_detectes', 'resume_journee')
        }),
    )
