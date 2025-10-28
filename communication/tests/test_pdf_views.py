# communication/tests/test_pdf_views.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
from communication.models import RapportPDF, ModeleRapport
from dashboard.models import Statistique

User = get_user_model()


class PDFGenerationViewsTestCase(TestCase):
    """Test cases for PDF generation views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test statistics
        self.statistique = Statistique.objects.create(
            utilisateur=self.user,
            periode="Janvier 2024",
            frequence_ecriture=15,
            score_humeur=7.5,
            themes_dominants=['travail', 'famille', 'sport'],
            bilan_mensuel="Un mois productif avec une bonne progression."
        )
    
    def test_generate_pdf_report_view(self):
        """Test PDF report generation view"""
        data = {
            'statistique_id': str(self.statistique.id),
            'titre': 'Test Rapport',
            'mois': 'Janvier 2024',
            'format_rapport': 'complet',
            'template_rapport': 'moderne',
            'couleur_principale': '#3498db',
            'inclure_statistiques': True,
            'inclure_graphiques': True
        }
        
        response = self.client.post(
            reverse('communication:generer_rapport'),  # ✅ Use namespace
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('rapport_id', response_data)
    
    def test_list_rapports_view(self):
        """Test listing user's reports view"""
        # Create a test report
        RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Test Rapport",
            mois="Janvier 2024"
        )
        
        response = self.client.get(reverse('communication:liste_rapports'))  # ✅ Use namespace
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('rapports', response_data)
        self.assertEqual(len(response_data['rapports']), 1)
    
    def test_duplicate_rapport_view(self):
        """Test duplicating a report view"""
        original = RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Original Rapport",
            mois="Janvier 2024"
        )
        
        response = self.client.post(
            reverse('communication:dupliquer_rapport', args=[original.id])  # ✅ Use namespace
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Check if duplicate was created
        duplicates = RapportPDF.objects.filter(titre__startswith="Copie de")
        self.assertEqual(duplicates.count(), 1)


class ModeleRapportTestCase(TestCase):
    """Test cases for report templates"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_modele_creation(self):
        """Test report template creation"""
        modele = ModeleRapport.objects.create(
            nom="Test Template",
            format_rapport='resume',
            template_rapport='minimaliste',
            public=True,
            configuration={'test': 'value'}
        )
        
        self.assertEqual(modele.nom, "Test Template")
        self.assertEqual(modele.format_rapport, 'resume')
        self.assertTrue(modele.public)