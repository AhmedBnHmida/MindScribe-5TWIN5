# communication/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from communication.models import RapportPDF, ModeleRapport, HistoriqueGeneration
from dashboard.models import Statistique

User = get_user_model()


class RapportPDFModelTestCase(TestCase):
    """Test cases for RapportPDF model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.statistique = Statistique.objects.create(
            utilisateur=self.user,
            periode="Janvier 2024",
            frequence_ecriture=15,
            score_humeur=7.5
        )
    
    def test_rapport_creation(self):
        """Test creating a PDF report"""
        rapport = RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Test Rapport",
            mois="Janvier 2024",
            format_rapport='complet',
            template_rapport='moderne'
        )
        
        self.assertEqual(rapport.titre, "Test Rapport")
        self.assertEqual(rapport.mois, "Janvier 2024")
        self.assertEqual(rapport.format_rapport, 'complet')
        self.assertEqual(rapport.statut, 'brouillon')
    
    def test_rapport_filename_generation(self):
        """Test PDF filename generation"""
        rapport = RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Test Rapport",
            mois="Janvier 2024"
        )
        
        filename = rapport.generer_nom_fichier()
        expected_pattern = f"rapport_janvier_2024_{rapport.id}.pdf"
        self.assertIn("rapport_janvier_2024", filename.lower())
        self.assertIn(".pdf", filename)
    
    def test_rapport_sections_actives(self):
        """Test active sections configuration"""
        rapport = RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Test Rapport",
            mois="Janvier 2024",
            inclure_statistiques=True,
            inclure_graphiques=False,
            inclure_analyse_ia=True
        )
        
        sections = rapport.get_sections_actives()
        self.assertTrue(sections['statistiques_cles'])
        self.assertFalse(sections['graphiques_evolution'])
        self.assertTrue(sections['analyse_humeur'])
    
    def test_rapport_est_pret_property(self):
        """Test est_pret property"""
        rapport = RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Test Rapport",
            mois="Janvier 2024",
            statut='termine'
        )
        
        # Without PDF file, should not be ready
        self.assertFalse(rapport.est_pret)
        
        # With PDF file, should be ready
        # Note: In real scenario, you'd mock the file field
        rapport.statut = 'termine'
        self.assertFalse(rapport.est_pret)  # Still false without actual file


class ModeleRapportModelTestCase(TestCase):
    """Test cases for ModeleRapport model"""
    
    def test_modele_creation(self):
        """Test creating a report template"""
        modele = ModeleRapport.objects.create(
            nom="Moderne Complet",
            format_rapport='complet',
            template_rapport='moderne',
            public=True,
            configuration={
                'couleur_principale': '#3498db',
                'inclure_statistiques': True
            }
        )
        
        self.assertEqual(modele.nom, "Moderne Complet")
        self.assertEqual(modele.format_rapport, 'complet')
        self.assertTrue(modele.public)
        self.assertIn('couleur_principale', modele.configuration)


class HistoriqueGenerationModelTestCase(TestCase):
    """Test cases for HistoriqueGeneration model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.statistique = Statistique.objects.create(
            utilisateur=self.user,
            periode="Janvier 2024"
        )
        
        self.rapport = RapportPDF.objects.create(
            utilisateur=self.user,
            statistique=self.statistique,
            titre="Test Rapport",
            mois="Janvier 2024"
        )
    
    def test_historique_creation(self):
        """Test creating generation history"""
        historique = HistoriqueGeneration.objects.create(
            rapport=self.rapport,
            statut='reussi',
            message_erreur=""
        )
        
        self.assertEqual(historique.rapport, self.rapport)
        self.assertEqual(historique.statut, 'reussi')
        self.assertIsNotNone(historique.date_debut)