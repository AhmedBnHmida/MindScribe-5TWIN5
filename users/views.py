from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def landing_page(request):
    return render(request, 'commun/landing.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirection basée sur le rôle
            if user.is_superuser:
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
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur existe déjà')
            else:
                user = User.objects.create_user(username, email, password)
                login(request, user)
                return redirect('users:home')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas')
    
    return render(request, 'auth/register.html')