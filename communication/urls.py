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
    path('assistant-ia/envoyer-message/', EnvoyerMessageView.as_view(), name='envoyer_message'),
    path('assistant-ia/historique/', HistoriqueConversationsView.as_view(), name='historique_conversations'),
    path('assistant-ia/session/<uuid:session_id>/', GetSessionView.as_view(), name='get_session'),
]

