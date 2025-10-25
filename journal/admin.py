from django.contrib import admin
from .models import Journal

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'date_creation', 'type_entree', 'categorie']
    list_filter = ['type_entree', 'date_creation', 'categorie']
    search_fields = ['utilisateur__username', 'utilisateur__email', 'contenu_texte', 'categorie']
    readonly_fields = ['id', 'date_creation']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'utilisateur', 'date_creation', 'categorie', 'type_entree')
        }),
        ('Contenu', {
            'fields': ('contenu_texte', 'audio', 'image')
        }),
    )
