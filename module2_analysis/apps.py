"""
App configuration for the module2_analysis app.
"""
from django.apps import AppConfig


class Module2AnalysisConfig(AppConfig):
    """
    Configuration for the module2_analysis app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'module2_analysis'
    verbose_name = 'Multimodal Journal Analysis'

    def ready(self):
        """
        Initialize app when Django starts.
        This is where we can load AI models to ensure they're loaded only once.
        """
        # Import services to trigger model loading
        # Note: This is commented out to avoid loading models during testing
        # from . import services

