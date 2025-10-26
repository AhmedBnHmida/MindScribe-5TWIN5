from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.journal_list, name='list'),
    path('create/', views.create_journal_entry, name='create'),
    path('<uuid:journal_id>/', views.journal_detail, name='detail'),
]

