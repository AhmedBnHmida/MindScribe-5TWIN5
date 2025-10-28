from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
import json

# Import des modèles avec gestion d'erreur
try:
    from dashboard.models import Statistique
except ImportError:
    print("⚠️  Modèle Statistique non trouvé dans dashboard")

try:
    from journal.models import Journal
except ImportError:
    print("⚠️  Modèle Journal non trouvé")

try:
    from analysis.models import AnalyseIA
except ImportError:
    print("⚠️  Modèle AnalyseIA non trouvé")

try:
    from recommendations.models import Recommandation, Objectif
except ImportError:
    print("⚠️  Modèles Recommandation/Objectif non trouvés")

from communication.models import RapportPDF, HistoriqueGeneration

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée des données de test complètes pour les rapports PDF'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Démarrage de la création des données de test...")
        
        # Créer ou récupérer l'utilisateur de test
        user = self._create_test_user()
        
        if not user:
            self.stdout.write(self.style.ERROR('❌ Échec de la création de l\'utilisateur de test'))
            return
        
        # Créer des statistiques de test
        statistique = self._create_test_statistics(user)
        
        # Créer des journaux et analyses de test (si les apps existent)
        self._create_test_journals_and_analyses(user, statistique)
        
        # Créer des recommandations de test (si l'app existe)
        self._create_test_recommendations(user, statistique)
        
        # Créer un rapport PDF de test
        rapport = self._create_test_pdf_report(user, statistique)
        
        self.stdout.write(self.style.SUCCESS('🎉 Données de test créées avec succès!'))
        self.stdout.write(f"👤 Utilisateur: {user.email}")
        if statistique:
            self.stdout.write(f"📊 Statistiques: {statistique.periode}")
        if rapport:
            self.stdout.write(f"📄 Rapport: {rapport.titre}")

    def _create_test_user(self):
        """Crée un utilisateur de test avec les champs exacts de CustomUser"""
        try:
            user, created = User.objects.get_or_create(
                email='test_pdf@mindscribe.com',
                defaults={
                    'username': 'testuser_pdf',
                    'first_name': 'Test',
                    'last_name': 'PDF',
                    'is_active': True,
                    'is_staff': False,
                    'role': 'user',
                    'phone_number': '+1234567890',
                    'langue': 'fr',
                    'age': 30,
                    'adresse': {'code_postal': '75001', 'ville': 'Paris', 'pays': 'France'},
                    'etat_civil': 'Célibataire',
                    'sexe': 'M',
                    'status_professionnel': 'travailleur',
                    'casanier': False,
                    'sociable': True,
                    'profession': 'Développeur',
                    'passions': ['programmation', 'lecture', 'sport'],
                    'objectifs_personnels': ['Apprendre Django', 'Améliorer la productivité'],
                    'routine_quotidienne': {'matinale': True, 'reguliere': True},
                    'humeur_generale': 'heureux',
                    'niveau_stress': 3,
                    'qualite_sommeil': 'bon',
                    'frequence_ecriture_souhaitee': 'soir',
                    'moment_prefere_ecriture': 'soir',
                    'niveau_activite_physique': 'modere',
                    'habitudes_alimentaires': 'equilibree',
                    'heures_sommeil_par_nuit': 7.5,
                    'centres_interet': ['technologie', 'psychologie', 'développement personnel'],
                    'preferences_suivi': {'notifications': True, 'rapports_automatiques': True}
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS('✅ Utilisateur de test PDF créé'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Utilisateur de test PDF existe déjà'))
            
            return user
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création utilisateur: {e}'))
            return None

    def _create_test_statistics(self, user):
        """Crée des statistiques de test réalistes"""
        try:
            from dashboard.models import Statistique
            
            # Créer des statistiques pour différents mois
            months_data = [
                {
                    'periode': 'Octobre 2025',
                    'frequence_ecriture': 18,
                    'score_humeur': 7.8,
                    'themes_dominants': ['productivité', 'bien-être', 'santé mentale', 'développement personnel'],
                    'bilan_mensuel': 'Mois très productif avec une amélioration notable de l\'humeur générale. Bon équilibre travail-vie personnelle.'
                },
                {
                    'periode': 'Septembre 2025', 
                    'frequence_ecriture': 12,
                    'score_humeur': 6.2,
                    'themes_dominants': ['stress', 'organisation', 'repos', 'sport'],
                    'bilan_mensuel': 'Mois chargé avec quelques périodes de stress. Bonne prise de conscience des besoins en repos.'
                },
                {
                    'periode': 'Août 2025',
                    'frequence_ecriture': 22,
                    'score_humeur': 8.5,
                    'themes_dominants': ['vacances', 'créativité', 'famille', 'loisirs'],
                    'bilan_mensuel': 'Excellent mois de vacances avec beaucoup de créativité et de moments en famille.'
                }
            ]
            
            created_stats = []
            for month_data in months_data:
                statistique, created = Statistique.objects.get_or_create(
                    utilisateur=user,
                    periode=month_data['periode'],
                    defaults=month_data
                )
                if created:
                    created_stats.append(statistique)
                    self.stdout.write(self.style.SUCCESS(f"✅ Statistiques {month_data['periode']} créées"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Statistiques {month_data['periode']} existent déjà"))
            
            return created_stats[0] if created_stats else Statistique.objects.filter(utilisateur=user).first()
            
        except ImportError:
            self.stdout.write(self.style.ERROR('❌ Modèle Statistique non disponible'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création statistiques: {e}'))
            return None

    def _create_test_journals_and_analyses(self, user, statistique):
        """Crée des journaux et analyses de test"""
        try:
            from journal.models import Journal
            from analysis.models import AnalyseIA
            
            # Données de test pour les journaux
            journal_entries = [
                {
                    'contenu': "Aujourd'hui, j'ai terminé mon projet MindScribe. Je me sens accompli et motivé pour la suite. La session de codage était très productive. J'ai résolu plusieurs problèmes complexes et j'ai hâte de voir les utilisateurs bénéficier de cette application.",
                    'ton': 'positif',
                    'mots_cles': ['projet', 'accomplissement', 'motivation', 'productivité', 'codage'],
                    'themes': ['travail', 'développement personnel', 'succès', 'technologie']
                },
                {
                    'contenu': "Journée un peu stressante au travail avec plusieurs deadlines. J'ai réussi à tout gérer mais je me sens fatigué. Besoin de me reposer ce weekend. J'ai quand même pris le temps de faire une petite promenade pour me détendre.",
                    'ton': 'neutre', 
                    'mots_cles': ['stress', 'travail', 'fatigue', 'repos', 'détente'],
                    'themes': ['travail', 'santé', 'équilibre', 'bien-être']
                },
                {
                    'contenu': "Super journée ! J'ai fait du sport le matin, rencontré des amis pour le déjeuner et passé une soirée tranquille à lire. Parfait équilibre entre activité sociale et temps personnel. J'ai lu un livre fascinant sur la psychologie cognitive.",
                    'ton': 'positif',
                    'mots_cles': ['sport', 'amis', 'lecture', 'équilibre', 'social'],
                    'themes': ['santé', 'social', 'loisirs', 'développement personnel']
                },
                {
                    'contenu': "Réflexion du jour : j'ai remarqué que ma productivité est meilleure quand je commence la journée par de l'exercice. Je vais essayer de maintenir cette routine. Aujourd'hui j'ai aussi médité 10 minutes, c'était très bénéfique.",
                    'ton': 'positif',
                    'mots_cles': ['réflexion', 'productivité', 'routine', 'exercice', 'méditation'],
                    'themes': ['routine', 'productivité', 'bien-être', 'développement personnel']
                },
                {
                    'contenu': "Un peu de nostalgie aujourd'hui en retrouvant de vieilles photos. Ça m'a fait réfléchir à mon parcours et à tout le chemin parcouru. Je suis reconnaissant pour les expériences qui m'ont façonné.",
                    'ton': 'neutre',
                    'mots_cles': ['nostalgie', 'réflexion', 'parcours', 'reconnaissance', 'mémoire'],
                    'themes': ['réflexion', 'émotions', 'développement personnel']
                }
            ]
            
            created_count = 0
            for i, entry_data in enumerate(journal_entries):
                # Créer le journal
                journal = Journal.objects.create(
                    utilisateur=user,
                    contenu_texte=entry_data['contenu'],
                    type_entree='texte',
                    categorie='réflexion',
                    date_creation=timezone.now() - timedelta(days=(len(journal_entries) - i))
                )
                
                # Créer l'analyse IA associée
                analyse = AnalyseIA.objects.create(
                    journal=journal,
                    ton_general=entry_data['ton'],
                    mots_cles=entry_data['mots_cles'],
                    themes_detectes=entry_data['themes'],
                    resume_journee=f"Journée caractérisée par {entry_data['themes'][0]} avec un ton {entry_data['ton']}. {entry_data['contenu'][:80]}..."
                )
                
                # Lier l'analyse aux statistiques si possible
                if statistique and hasattr(statistique, 'analyses_liees'):
                    statistique.analyses_liees.add(analyse)
                
                created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✅ {created_count} journaux et analyses créés'))
            
        except ImportError as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Journal/Analysis non disponibles: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création journaux: {e}'))

    def _create_test_recommendations(self, user, statistique):
        """Crée des recommandations de test"""
        try:
            from recommendations.models import Recommandation, Objectif
            
            # Créer des recommandations
            recommendations = [
                {
                    'type': 'bien_etre',
                    'contenu': 'Pratiquez 10 minutes de méditation par jour pour réduire le stress et améliorer la concentration. Votre humeur générale en bénéficiera.',
                    'statut': 'nouvelle'
                },
                {
                    'type': 'productivite', 
                    'contenu': 'Essayez la technique Pomodoro (25min travail / 5min pause) pour booster votre productivité. Parfait pour vos sessions de codage.',
                    'statut': 'suivie'
                },
                {
                    'type': 'sommeil',
                    'contenu': 'Maintenez une routine de sommeil régulière avec 7-8 heures par nuit pour une meilleure récupération. Votre qualité de sommeil est déjà bonne, continuez !',
                    'statut': 'nouvelle'
                },
                {
                    'type': 'nutrition',
                    'contenu': 'Intégrez plus de fruits et légumes dans votre alimentation. Votre habitude équilibrée est excellente, quelques ajustements pourraient optimiser votre énergie.',
                    'statut': 'nouvelle'
                }
            ]
            
            for rec_data in recommendations:
                Recommandation.objects.create(
                    utilisateur=user,
                    statistique=statistique,
                    type=rec_data['type'],
                    contenu=rec_data['contenu'],
                    statut=rec_data['statut'],
                    date_emission=timezone.now() - timedelta(days=10)
                )
            
            # Créer des objectifs
            objectifs = [
                {
                    'nom': 'Écrire 3 fois par semaine',
                    'description': 'Maintenir une régularité dans l\'écriture du journal pour mieux suivre mon évolution personnelle',
                    'progres': 75.0,
                    'date_debut': timezone.now() - timedelta(days=30),
                    'date_fin': timezone.now() + timedelta(days=60)
                },
                {
                    'nom': 'Apprendre Django avancé',
                    'description': 'Maîtriser les concepts avancés de Django pour améliorer MindScribe',
                    'progres': 40.0,
                    'date_debut': timezone.now() - timedelta(days=45),
                    'date_fin': timezone.now() + timedelta(days=90)
                },
                {
                    'nom': 'Améliorer la routine matinale',
                    'description': 'Intégrer méditation et exercice dans ma routine du matin',
                    'progres': 60.0,
                    'date_debut': timezone.now() - timedelta(days=15),
                    'date_fin': timezone.now() + timedelta(days=45)
                }
            ]
            
            for obj_data in objectifs:
                Objectif.objects.create(
                    utilisateur=user,
                    nom=obj_data['nom'],
                    description=obj_data['description'],
                    progres=obj_data['progres'],
                    date_debut=obj_data['date_debut'],
                    date_fin=obj_data['date_fin']
                )
            
            self.stdout.write(self.style.SUCCESS('✅ Recommandations et objectifs créés'))
            
        except ImportError:
            self.stdout.write(self.style.WARNING('⚠️ Recommendations non disponibles'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création recommandations: {e}'))

    def _create_test_pdf_report(self, user, statistique):
        """Crée un rapport PDF de test avec génération réelle du PDF"""
        if not statistique:
            self.stdout.write(self.style.ERROR('❌ Impossible de créer un rapport sans statistiques'))
            return None
        
        try:
            # Vérifier si un rapport existe déjà pour ces statistiques
            existing_rapport = RapportPDF.objects.filter(statistique=statistique).first()
            if existing_rapport:
                self.stdout.write(self.style.WARNING('⚠️ Rapport PDF existe déjà'))
                return existing_rapport
            
            # Créer un nouveau rapport avec statut "en_cours"
            rapport = RapportPDF.objects.create(
                utilisateur=user,
                statistique=statistique,
                titre=f"Rapport Détaillé {statistique.periode}",
                mois=statistique.periode,
                description=f"Rapport de test complet pour {statistique.periode} avec toutes les sections activées.",
                format_rapport='complet',
                template_rapport='moderne',
                couleur_principale='#3498db',
                couleur_secondaire='#2c3e50',
                inclure_statistiques=True,
                inclure_graphiques=True,
                inclure_analyse_ia=True,
                inclure_journaux=True,
                inclure_objectifs=True,
                inclure_recommandations=True,
                statut='en_cours'  # ✅ Change to 'en_cours' to trigger generation
            )
            
            # ✅ CRITICAL: Actually generate the PDF file
            self._generate_pdf_for_report(rapport)
            
            self.stdout.write(self.style.SUCCESS('✅ Rapport PDF de test créé avec fichier PDF généré'))
            return rapport
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création rapport PDF: {e}'))
            return None

    def _generate_pdf_for_report(self, rapport):
        """Generate actual PDF file for the report"""
        try:
            from django.core.files.base import ContentFile
            from communication.services.pdf_generator import PDFGenerationService
            
            self.stdout.write("🔄 Génération du fichier PDF...")
            
            # Create generation history
            historique = HistoriqueGeneration.objects.create(
                rapport=rapport,
                statut='debute'
            )
            
            # Generate PDF using your service
            pdf_service = PDFGenerationService()
            pdf_content = pdf_service.generate_complete_report(rapport)
            
            # Save PDF to FileField
            filename = rapport.generer_nom_fichier()
            rapport.contenu_pdf.save(filename, ContentFile(pdf_content))
            
            # Update status to completed
            rapport.statut = 'termine'
            rapport.save()
            
            # Update history
            historique.statut = 'reussi'
            historique.date_fin = timezone.now()
            historique.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ PDF généré: {filename}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur génération PDF: {e}'))
            
            # Update status to error
            rapport.statut = 'erreur'
            rapport.save()
            
            if 'historique' in locals():
                historique.statut = 'echoue'
                historique.message_erreur = str(e)
                historique.date_fin = timezone.now()
                historique.save()