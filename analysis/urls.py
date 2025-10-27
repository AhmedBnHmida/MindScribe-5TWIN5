from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # API endpoints
    path('api/analyse/', views.analyse_api_view, name='api_analyse'),
]

