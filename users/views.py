from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser  
from .forms import CustomUserChangeForm

# Create your views here.

def landing_page(request):
    return render(request, 'commun/landing.html')

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username']  # Peut être username ou email
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
            # Redirection basée sur le rôle
            if user.is_superuser or user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect('users:home')
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:landing')

@login_required
def home(request):
    return render(request, 'views/users/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        
        if password == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà')
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Cette adresse email est déjà utilisée')
            else:
                # Créer un CustomUser avec tous les champs
                user = CustomUser.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number
                )
                login(request, user)
                messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
                return redirect('users:home')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas')
    
    return render(request, 'auth/register.html')



@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('users:home')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'views/users/edit_profile.html', {'form': form})