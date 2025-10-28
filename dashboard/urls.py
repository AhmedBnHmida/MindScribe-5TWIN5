# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.tableau_bord, name='tableau_bord'),
    
    # APIs pour les données
    path('api/evolution-humeur/', views.donnees_evolution_humeur, name='api_evolution_humeur'),
    path('api/wordcloud/', views.donnees_wordcloud, name='api_wordcloud'),
    path('api/themes/', views.donnees_themes, name='api_themes'),
    path('api/chronologie/', views.donnees_chronologie, name='api_chronologie'),
    path('api/statistiques/', views.donnees_statistiques, name='api_statistiques'),
    path('api/distribution-humeurs/', views.donnees_distribution_humeurs, name='api_distribution_humeurs'),
    path('api/frequence-ecriture/', views.donnees_frequence_ecriture, name='api_frequence_ecriture'),
    path('api/score-emotionnel/', views.donnees_score_emotionnel, name='api_score_emotionnel'),

# URLs pour les bilans mensuels
path('bilan-mensuel/', views.bilan_mensuel, name='bilan_mensuel'),


 path('', views.tableau_bord, name='tableau_bord'),  # ou le nom correct
    path('bilan-mensuel/<int:annee>/<int:mois>/', views.bilan_mensuel, name='bilan_mensuel_detail'),
    path('api/generer-bilan/', views.generer_bilan_api, name='generer_bilan_api'),









      # Analyse rapide
    path('analyse-rapide/', views.analyse_rapide, name='analyse_rapide'),
   
  # API d'analyse rapide
    path('api/analyser-rapide/', views.analyser_texte_rapide, name='analyser_texte_rapide'),
    path('api/sauvegarder-analyse/', views.sauvegarder_analyse_rapide, name='sauvegarder_analyse_rapide'),






   
    path('api/analyse-details/<uuid:analysis_id>/', views.analyse_details, name='analyse_details'),


]