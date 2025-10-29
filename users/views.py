from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser  
from .forms import CustomUserChangeForm
import json

# Create your views here.

def landing_page(request):
    """Page d'accueil/landing"""
    return render(request, 'commun/landing.html')



def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username']
        password = request.POST['password']
        
        # Essayer d'authentifier avec username
        user = authenticate(request, username=username_or_email, password=password)
        
        # Si échec, essayer avec email
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
        
        if user is not None:
            login(request, user)
            
            # ⚠️ CORRECTION ICI - Utilise le paramètre 'next'
            next_url = request.POST.get('next') or request.GET.get('next')
            
            # Redirection basée sur le rôle ET le paramètre next
            if user.is_superuser or user.role == 'admin' or user.is_admin_user:
                return redirect(next_url or '/admin/')
            else:
                # 🔥 CHANGEMENT ICI : Redirige vers dashboard au lieu de home
                return redirect(next_url or 'dashboard:tableau_bord')  # 👈 MODIFIÉ
        else:
            messages.error(request, 'Identifiants invalides')
    
    # Passe le paramètre 'next' au template
    context = {}
    if 'next' in request.GET:
        context['next'] = request.GET['next']
    
    return render(request, 'auth/login.html', context)






@login_required
def logout_view(request):
    logout(request)
    return redirect('users:landing')

@login_required
def home(request):
    # Vous pouvez accéder à tous les nouveaux champs via request.user
    # Par exemple : request.user.humeur_generale, request.user.qualite_sommeil, etc.
    return render(request, 'views/d')





def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        
        # Basic fields
        age = request.POST.get('age', None)
        sexe = request.POST.get('sexe', '')
        status_professionnel = request.POST.get('status_professionnel', '')
        profession = request.POST.get('profession', '')
        etat_civil = request.POST.get('etat_civil', '')
        langue = request.POST.get('langue', 'fr')
        
        # Personality traits
        casanier = 'casanier' in request.POST
        sociable = 'sociable' in request.POST
        
        # Well-being fields
        humeur_generale = request.POST.get('humeur_generale', 'neutre')
        niveau_stress = request.POST.get('niveau_stress', 5)
        qualite_sommeil = request.POST.get('qualite_sommeil', 'moyen')
        heures_sommeil_par_nuit = request.POST.get('heures_sommeil_par_nuit', 7.0)
        
        # Activity and habits
        niveau_activite_physique = request.POST.get('niveau_activite_physique', 'sedentaire')
        habitudes_alimentaires = request.POST.get('habitudes_alimentaires', 'equilibree')
        
        # Writing preferences
        frequence_ecriture_souhaitee = request.POST.get('frequence_ecriture_souhaitee', 'variable')
        moment_prefere_ecriture = request.POST.get('moment_prefere_ecriture', 'variable')
        
        # JSON fields
        centres_interet = request.POST.get('centres_interet', '')
        passions = request.POST.get('passions', '')


         # Récupérer les champs d'adresse
        adresse_rue = request.POST.get('adresse_rue', '')
        adresse_ville = request.POST.get('adresse_ville', '')
        adresse_code_postal = request.POST.get('adresse_code_postal', '')
        adresse_province = request.POST.get('adresse_province', '')
        adresse_pays = request.POST.get('adresse_pays', 'Tunisie')
        
        
        if password == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà')
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Cette adresse email est déjà utilisée')
            else:
                # Handle conversions
                try:
                    age_int = int(age) if age else None
                except (ValueError, TypeError):
                    age_int = None
                
                try:
                    niveau_stress_int = int(niveau_stress) if niveau_stress else 5
                except (ValueError, TypeError):
                    niveau_stress_int = 5
                
                try:
                    heures_sommeil_float = float(heures_sommeil_par_nuit) if heures_sommeil_par_nuit else 7.0
                except (ValueError, TypeError):
                    heures_sommeil_float = 7.0
                
                # Process JSON fields
                centres_interet_list = [item.strip() for item in centres_interet.split(',') if item.strip()] if centres_interet else []
                passions_list = [item.strip() for item in passions.split(',') if item.strip()] if passions else []
                
                # CORRECTION : Créer l'utilisateur avec create_user d'abord, puis mettre à jour les champs supplémentaires
                user = CustomUser.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password
                )
                
                # CORRECTION : Mettre à jour tous les champs supplémentaires
                user.first_name = first_name
                user.last_name = last_name
                user.phone_number = phone_number
                user.age = age_int
                user.sexe = sexe
                user.status_professionnel = status_professionnel
                user.profession = profession
                user.etat_civil = etat_civil
                user.langue = langue
                user.casanier = casanier
                user.sociable = sociable
                user.humeur_generale = humeur_generale
                user.niveau_stress = niveau_stress_int
                user.qualite_sommeil = qualite_sommeil
                user.heures_sommeil_par_nuit = heures_sommeil_float
                user.niveau_activite_physique = niveau_activite_physique
                user.habitudes_alimentaires = habitudes_alimentaires
                user.frequence_ecriture_souhaitee = frequence_ecriture_souhaitee
                user.moment_prefere_ecriture = moment_prefere_ecriture
                user.centres_interet = centres_interet_list
                user.passions = passions_list
                

                # NOUVEAU : Construire l'objet adresse JSON
                adresse_data = {}
                if adresse_rue:
                    adresse_data['rue'] = adresse_rue
                if adresse_ville:
                    adresse_data['ville'] = adresse_ville
                if adresse_code_postal:
                    adresse_data['code_postal'] = adresse_code_postal
                if adresse_province:
                    adresse_data['province'] = adresse_province
                if adresse_pays:
                    adresse_data['pays'] = adresse_pays
                
                user.adresse = adresse_data
                # CORRECTION : Initialiser les champs JSON manquants
                user.preferences_suivi = {}
                
                user.routine_quotidienne = {}
                user.objectifs_personnels = []
                
                # Handle photo upload
                if 'photo' in request.FILES:
                    user.photo = request.FILES['photo']
                
                # CORRECTION : Sauvegarder l'utilisateur après avoir défini tous les champs
                user.save()
                
                login(request, user)
                messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
                return redirect('dashboard:tableau_bord')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas')
    
    return render(request, 'auth/register.html')




@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'views/users/edit_profile.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
        'personality_traits': {
            'casanier': user.casanier,
            'sociable': user.sociable,
        },
        'well_being': {
            'humeur_generale': user.get_humeur_generale_display(),
            'niveau_stress': user.niveau_stress,
            'qualite_sommeil': user.get_qualite_sommeil_display(),
            'heures_sommeil_par_nuit': user.heures_sommeil_par_nuit,
        },
        'activity': {
            'niveau_activite_physique': user.get_niveau_activite_physique_display(),
            'habitudes_alimentaires': user.get_habitudes_alimentaires_display(),
        },
        'writing_preferences': {
            'frequence_ecriture_souhaitee': user.get_frequence_ecriture_souhaitee_display(),
            'moment_prefere_ecriture': user.get_moment_prefere_ecriture_display(),
        }
    }
    return render(request, 'views/users/profile.html', context)