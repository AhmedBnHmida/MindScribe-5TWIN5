# dashboard/services/__init__.py
from .bilan_ia import ServiceBilanIA
from .analyse_ia import AnalyseurRapide
from .sauvegarde_analyse import ServiceSauvegardeAnalyse

__all__ = [
    'ServiceBilanIA',
    'AnalyseurRapide', 
    'ServiceSauvegardeAnalyse'
]