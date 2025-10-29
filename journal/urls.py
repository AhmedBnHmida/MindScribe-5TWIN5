from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.journal_list, name='list'),
    path('create/', views.create_journal_entry, name='create'),
    path('<uuid:journal_id>/', views.journal_detail, name='detail'),
    path('<uuid:journal_id>/edit/', views.edit_journal, name='edit'),
    path('<uuid:journal_id>/delete/', views.delete_journal, name='delete'),
    path('old/<uuid:journal_id>/edit/', views.edit_old_journal, name='edit_old'),
    path('old/<uuid:journal_id>/delete/', views.delete_old_journal, name='delete_old'),
]

