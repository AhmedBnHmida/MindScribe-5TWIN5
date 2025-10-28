from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from communication.models import SuggestionConnexion
from communication.services.suggestion_service import SuggestionConnexionService

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée deux utilisateurs de test pour tester les suggestions de connexion avec la logique améliorée'

    def handle(self, *args, **options):
        self.stdout.write("Creating test users for suggestion system testing...")
        
        # Créer le premier utilisateur (Alice) - avec profil qui matche bien avec Bob
        user1 = self._create_user(
            email='alice@test.com',
            username='alice_test',
            first_name='Alice',
            last_name='Test',
            profession='Développeuse',
            passions=['programmation', 'lecture', 'voyage'],
            objectifs_personnels=['Apprendre Django', 'Voyager plus', 'Méditation quotidienne'],
            centres_interet=['Programmation', 'Yoga', 'Lecture', 'Photographie'],
            humeur_generale='heureux'
        )
        
        # Créer le deuxième utilisateur (Bob) - avec profil similaire à Alice
        user2 = self._create_user(
            email='bob@test.com', 
            username='bob_test',
            first_name='Bob',
            last_name='Test',
            profession='Développeur',
            passions=['code', 'fitness', 'lecture'],
            objectifs_personnels=['Apprendre Python', 'Fitness', 'Lire plus'],
            centres_interet=['Programmation', 'Fitness', 'Lecture'],
            humeur_generale='heureux'
        )
        
        if not user1 or not user2:
            self.stdout.write(self.style.ERROR('Failed to create test users'))
            return
        
        # Créer des journaux de test pour les utilisateurs
        self._create_test_journals(user1, user2)
        
        # Calculer la similarité réelle avec le service amélioré
        self.stdout.write("\n[INFO] Calculating real similarity between Alice and Bob...")
        similarity_data = SuggestionConnexionService.calculate_similarity(user1, user2)
        self.stdout.write(f"  Overall Score: {similarity_data['overall_score']:.2%}")
        self.stdout.write(f"  Match Type: {similarity_data['type']}")
        
        # Créer des suggestions avec les scores réels
        self._create_suggestions(user1, user2, similarity_data)
        
        # Optionally generate more suggestions using the service
        try:
            self.stdout.write("\n[INFO] Generating additional suggestions for Alice...")
            count = SuggestionConnexionService.generate_suggestions_for_user(user1, max_suggestions=5)
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  Generated {count} additional suggestions"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Could not generate additional suggestions: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Test users created successfully!'))
        self.stdout.write(f"  Alice: {user1.email} / password: testpass123")
        self.stdout.write(f"  Bob: {user2.email} / password: testpass123")
        self.stdout.write("\n[INFO] Test instructions:")
        self.stdout.write("  1. Login with Alice (alice@test.com)")
        self.stdout.write("  2. Go to /communication/suggestions/")
        self.stdout.write("  3. See the suggestion with compatibility score")
        self.stdout.write("  4. Click on suggestion to see detailed breakdown")
        self.stdout.write("  5. Accept the suggestion")
        self.stdout.write("  6. Login with Bob to see the connection")

    def _create_user(self, email, username, first_name, last_name, profession, passions, 
                     objectifs_personnels, centres_interet=None, humeur_generale='heureux'):
        """Crée un utilisateur de test avec profil complet"""
        try:
            # Default centres_interet if not provided
            if centres_interet is None:
                centres_interet = ['technologie', 'développement personnel']
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'is_staff': False,
                    'role': 'user',
                    'langue': 'fr',
                    'age': 28,
                    'profession': profession,
                    'passions': passions,
                    'objectifs_personnels': objectifs_personnels,
                    'centres_interet': centres_interet,
                    'humeur_generale': humeur_generale,
                    'niveau_stress': 2,
                    'qualite_sommeil': 'bon',
                    'frequence_ecriture_souhaitee': 'soir',
                    'moment_prefere_ecriture': 'soir',
                    'niveau_activite_physique': 'modere',
                    'habitudes_alimentaires': 'equilibree',
                    'heures_sommeil_par_nuit': 8.0,
                    'preferences_suivi': {'notifications': True, 'rapports_automatiques': True}
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'[OK] User {username} created'))
            else:
                # Update existing user with new profile data
                user.objectifs_personnels = objectifs_personnels
                user.centres_interet = centres_interet
                user.humeur_generale = humeur_generale
                user.passions = passions
                user.profession = profession
                user.save()
                self.stdout.write(self.style.WARNING(f'[INFO] User {username} already exists, profile updated'))
            
            return user
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error creating user {username}: {e}'))
            return None

    def _create_suggestions(self, user1, user2, similarity_data):
        """Crée des suggestions de connexion avec les scores réels calculés"""
        try:
            # Clean existing suggestions first
            SuggestionConnexion.objects.filter(
                utilisateur_source=user1,
                utilisateur_cible=user2
            ).delete()
            SuggestionConnexion.objects.filter(
                utilisateur_source=user2,
                utilisateur_cible=user1
            ).delete()
            
            # Suggestion de Alice vers Bob avec score réel
            suggestion1, created1 = SuggestionConnexion.objects.get_or_create(
                utilisateur_source=user1,
                utilisateur_cible=user2,
                defaults={
                    'score_similarite': similarity_data['overall_score'],
                    'type_suggestion': similarity_data['type'],
                    'statut': 'proposee',
                    'date_suggestion': timezone.now() - timedelta(days=1)
                }
            )
            
            if created1:
                self.stdout.write(self.style.SUCCESS(f'[OK] Suggestion Alice -> Bob created'))
                self.stdout.write(f'     Score: {suggestion1.score_similarite:.2%}, Type: {suggestion1.get_type_suggestion_display()}')
            else:
                # Update with real scores
                suggestion1.score_similarite = similarity_data['overall_score']
                suggestion1.type_suggestion = similarity_data['type']
                suggestion1.save()
                self.stdout.write(self.style.SUCCESS(f'[OK] Suggestion Alice -> Bob updated with real score'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error creating suggestions: {e}'))

    def _create_test_journals(self, user1, user2):
        """Crée des journaux de test pour les utilisateurs"""
        try:
            from journal.models import Journal
            
            # Journaux pour Alice
            alice_journals = [
                "Aujourd'hui j'ai terminé mon projet Django. Je me sens très satisfaite du résultat et j'ai appris beaucoup de nouvelles choses sur les modèles et les vues.",
                "Journée productive au travail. J'ai résolu plusieurs bugs complexes et l'équipe était contente de mes contributions. Je me sens motivée pour continuer.",
                "Super journée ! J'ai fait du sport le matin, puis j'ai lu un livre fascinant sur la programmation. L'équilibre travail-loisirs est important pour moi.",
                "Réflexion du jour : j'ai remarqué que ma productivité est meilleure quand je commence par une petite marche. Je vais essayer de maintenir cette routine.",
                "Un peu stressée aujourd'hui avec plusieurs deadlines, mais j'ai réussi à tout gérer. Une bonne nuit de sommeil m'aidera à récupérer."
            ]
            
            # Journaux pour Bob
            bob_journals = [
                "Nouveau projet de design en cours. J'adore créer des interfaces utilisateur intuitives et belles. L'art et la technologie se rencontrent parfaitement.",
                "Journée créative ! J'ai travaillé sur une nouvelle palette de couleurs et j'ai été inspiré par l'art moderne. La créativité coule naturellement aujourd'hui.",
                "Écoute de musique classique en travaillant. Ça m'aide à me concentrer et à être plus créatif. La musique est vraiment une source d'inspiration.",
                "Réflexion sur mon parcours de designer. J'ai parcouru un long chemin et je suis fier de mes réalisations. L'apprentissage continu est la clé.",
                "Petit coup de blues aujourd'hui, mais c'est normal. Demain sera meilleur. L'important c'est de garder une attitude positive."
            ]
            
            # Créer les journaux pour Alice
            for i, content in enumerate(alice_journals):
                Journal.objects.create(
                    utilisateur=user1,
                    contenu_texte=content,
                    type_entree='texte',
                    categorie='réflexion',
                    date_creation=timezone.now() - timedelta(days=i+1)
                )
            
            # Créer les journaux pour Bob
            for i, content in enumerate(bob_journals):
                Journal.objects.create(
                    utilisateur=user2,
                    contenu_texte=content,
                    type_entree='texte',
                    categorie='réflexion',
                    date_creation=timezone.now() - timedelta(days=i+1)
                )
            
            self.stdout.write(self.style.SUCCESS('[OK] Test journals created for Alice and Bob'))
            
        except ImportError:
            self.stdout.write(self.style.WARNING('[INFO] Journal model not available'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error creating journals: {e}'))
