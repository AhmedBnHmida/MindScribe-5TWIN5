from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.tableau_bord, name='tableau_bord'),
    path('api/evolution-humeur/', views.donnees_evolution_humeur, name='api_evolution_humeur'),
    path('api/wordcloud/', views.donnees_wordcloud, name='api_wordcloud'),
    path('api/themes/', views.donnees_themes, name='api_themes'),
    path('api/chronologie/', views.donnees_chronologie, name='api_chronologie'),
]