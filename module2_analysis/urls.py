"""
URL configuration for the module2_analysis app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'module2_analysis'

# Create a router for viewsets
router = DefaultRouter()
router.register(r'analyses', views.JournalAnalysisViewSet)

urlpatterns = [
    # API endpoints
    path('api/analyse/v2/', views.analyse_api_view, name='api_analyse'),
    
    # Detail view for analysis
    path('analysis/<uuid:analysis_id>/', views.analysis_detail_view, name='analysis_detail'),
    
    # ViewSet URLs
    path('api/', include(router.urls)),
]
