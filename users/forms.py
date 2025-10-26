from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
import json

class CustomUserChangeForm(UserChangeForm):
    # Add help texts and widgets for better display
    centres_interet = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Séparez par des virgules'}),
        help_text="Séparez par des virgules"
    )
    
    passions = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Séparez par des virgules'}),
        help_text="Séparez par des virgules"
    )
    
    objectifs_personnels = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Séparez par des virgules'}),
        help_text="Séparez par des virgules"
    )
    
    # Add fields for JSON data that might be stored as strings
    adresse_json = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Format JSON: {"rue": "...", "ville": "...", "code_postal": "..."}'}),
        help_text="Entrez l'adresse au format JSON"
    )
    
    preferences_suivi_json = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Format JSON: {"preference1": "valeur", "preference2": "valeur"}'}),
        help_text="Entrez les préférences au format JSON"
    )
    
    routine_quotidienne_json = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Format JSON: {"matinale": "...", "nocturne": "..."}'}),
        help_text="Entrez la routine au format JSON"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone_number', 'photo',
            'age', 'sexe', 'status_professionnel', 'profession', 'centres_interet',
            'preferences_suivi', 'langue', 'adresse', 'etat_civil', 'casanier',
            'sociable', 'passions', 'objectifs_personnels', 'routine_quotidienne',
            'humeur_generale', 'niveau_stress', 'qualite_sommeil',
            'frequence_ecriture_souhaitee', 'moment_prefere_ecriture',
            'niveau_activite_physique', 'habitudes_alimentaires', 'heures_sommeil_par_nuit'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'etat_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau_stress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '10'}),
            'heures_sommeil_par_nuit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'status_professionnel': forms.Select(attrs={'class': 'form-control'}),
            'humeur_generale': forms.Select(attrs={'class': 'form-control'}),
            'qualite_sommeil': forms.Select(attrs={'class': 'form-control'}),
            'frequence_ecriture_souhaitee': forms.Select(attrs={'class': 'form-control'}),
            'moment_prefere_ecriture': forms.Select(attrs={'class': 'form-control'}),
            'niveau_activite_physique': forms.Select(attrs={'class': 'form-control'}),
            'habitudes_alimentaires': forms.Select(attrs={'class': 'form-control'}),
            'langue': forms.Select(attrs={'class': 'form-control'}),
            'casanier': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sociable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from the form
        if 'password' in self.fields:
            del self.fields['password']
        
        # Convert JSON fields to string for display
        if self.instance:
            # List fields
            if self.instance.centres_interet:
                self.initial['centres_interet'] = ', '.join(self.instance.centres_interet)
            
            if self.instance.passions:
                self.initial['passions'] = ', '.join(self.instance.passions)
            
            if self.instance.objectifs_personnels:
                self.initial['objectifs_personnels'] = ', '.join(self.instance.objectifs_personnels)
            
            # JSON fields
            if self.instance.adresse:
                self.initial['adresse_json'] = json.dumps(self.instance.adresse, ensure_ascii=False, indent=2)
            
            if self.instance.preferences_suivi:
                self.initial['preferences_suivi_json'] = json.dumps(self.instance.preferences_suivi, ensure_ascii=False, indent=2)
            
            if self.instance.routine_quotidienne:
                self.initial['routine_quotidienne_json'] = json.dumps(self.instance.routine_quotidienne, ensure_ascii=False, indent=2)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Convert string fields back to JSON lists
        centres_interet = self.cleaned_data.get('centres_interet', '')
        if centres_interet:
            user.centres_interet = [item.strip() for item in centres_interet.split(',') if item.strip()]
        else:
            user.centres_interet = []
        
        passions = self.cleaned_data.get('passions', '')
        if passions:
            user.passions = [item.strip() for item in passions.split(',') if item.strip()]
        else:
            user.passions = []
        
        objectifs_personnels = self.cleaned_data.get('objectifs_personnels', '')
        if objectifs_personnels:
            user.objectifs_personnels = [item.strip() for item in objectifs_personnels.split(',') if item.strip()]
        else:
            user.objectifs_personnels = []
        
        # Convert JSON string fields back to Python objects
        adresse_json = self.cleaned_data.get('adresse_json', '')
        if adresse_json:
            try:
                user.adresse = json.loads(adresse_json)
            except json.JSONDecodeError:
                # If invalid JSON, store as empty dict
                user.adresse = {}
        else:
            user.adresse = {}
        
        preferences_suivi_json = self.cleaned_data.get('preferences_suivi_json', '')
        if preferences_suivi_json:
            try:
                user.preferences_suivi = json.loads(preferences_suivi_json)
            except json.JSONDecodeError:
                user.preferences_suivi = {}
        else:
            user.preferences_suivi = {}
        
        routine_quotidienne_json = self.cleaned_data.get('routine_quotidienne_json', '')
        if routine_quotidienne_json:
            try:
                user.routine_quotidienne = json.loads(routine_quotidienne_json)
            except json.JSONDecodeError:
                user.routine_quotidienne = {}
        else:
            user.routine_quotidienne = {}
        
        if commit:
            user.save()
        
        return user