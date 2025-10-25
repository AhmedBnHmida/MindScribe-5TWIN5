from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Session

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = ['username', 'email', 'phone_number', 'role', 'age', 'humeur_generale', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff', 'sexe', 'status_professionnel', 'humeur_generale']
    search_fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations de base', {
            'fields': ('role', 'phone_number', 'photo', 'uuid')
        }),
        ('Informations personnelles', {
            'fields': ('age', 'sexe', 'etat_civil', 'adresse', 'langue', 'centres_interet')
        }),
        ('Profession et passions', {
            'fields': ('status_professionnel', 'profession', 'passions', 'objectifs_personnels')
        }),
        ('Traits de personnalité', {
            'fields': ('casanier', 'sociable')
        }),
        ('Bien-être et santé', {
            'fields': ('humeur_generale', 'niveau_stress', 'qualite_sommeil', 'heures_sommeil_par_nuit', 
                      'niveau_activite_physique', 'habitudes_alimentaires')
        }),
        ('Préférences d\'écriture', {
            'fields': ('frequence_ecriture_souhaitee', 'moment_prefere_ecriture')
        }),
        ('Routine', {
            'fields': ('routine_quotidienne', 'preferences_suivi')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'phone_number', 'role')
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'date_connexion', 'adresse_ip', 'actif']
    list_filter = ['actif', 'date_connexion']
    search_fields = ['utilisateur__username', 'utilisateur__email', 'adresse_ip']
    readonly_fields = ['id', 'date_connexion']