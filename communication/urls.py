from django.urls import path
from .views import (
    DashboardCommunicationView,
    GenererRapportPDFView,
    ListeRapportsView,
    TelechargerRapportView,
    ApercuRapportView,
    DupliquerRapportView,
    SupprimerRapportView,
    AssistantIAView,
    EnvoyerMessageView,
    HistoriqueConversationsView,
    GetSessionView,
    RefreshJournalsView,
    SuggestionsConnexionView,
    AccepterSuggestionView,
    IgnorerSuggestionView,
    GenererSuggestionsView,
    SupprimerConnexionView,
    VoirProfilView,
)

app_name = 'communication'

urlpatterns = [

     path('', DashboardCommunicationView.as_view(), name='dashboard'),
    # Add your communication URLs here
    # Example:
    # path('reports/', views.list_reports, name='reports'),
    # path('assistant/', views.assistant_chat, name='assistant'),
    # path('connections/', views.suggestions, name='suggestions'),

    # PDF Generation URLs
    path('rapports/generer/', GenererRapportPDFView.as_view(), name='generer_rapport'),
    path('rapports/', ListeRapportsView.as_view(), name='liste_rapports'),  # Template view
    path('rapports/<uuid:rapport_id>/telecharger/', TelechargerRapportView.as_view(), name='telecharger_rapport'),
    path('rapports/<uuid:rapport_id>/apercu/', ApercuRapportView.as_view(), name='apercu_rapport'),
    path('rapports/<uuid:rapport_id>/dupliquer/', DupliquerRapportView.as_view(), name='dupliquer_rapport'),
    path('rapports/<uuid:rapport_id>/supprimer/', SupprimerRapportView.as_view(), name='supprimer_rapport'),


    # URLs Assistant IA
    path('assistant-ia/', AssistantIAView.as_view(), name='assistant_ia'),
    path('assistant-ia/envoyer_message/', EnvoyerMessageView.as_view(), name='envoyer_message'),
    path('assistant-ia/historique/', HistoriqueConversationsView.as_view(), name='historique_conversations'),
    path('assistant-ia/session/<str:session_id>/', GetSessionView.as_view(), name='session_history'),
    path('assistant-ia/refresh-journals/', RefreshJournalsView.as_view(), name='refresh_journals'),

    # URLs Suggestions de Connexion
    path('suggestions/', SuggestionsConnexionView.as_view(), name='suggestions'),
    path('suggestions/<uuid:suggestion_id>/accepter/', AccepterSuggestionView.as_view(), name='accepter_suggestion'),
    path('suggestions/<uuid:suggestion_id>/ignorer/', IgnorerSuggestionView.as_view(), name='ignorer_suggestion'),
    path('suggestions/<uuid:suggestion_id>/supprimer/', SupprimerConnexionView.as_view(), name='supprimer_connexion'),
    path('suggestions/generer/', GenererSuggestionsView.as_view(), name='generer_suggestions'),
    
    # URLs Profil utilisateur
    path('profil/<int:user_id>/', VoirProfilView.as_view(), name='voir_profil'),
]

