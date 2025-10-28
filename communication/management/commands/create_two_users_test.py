from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from communication.models import SuggestionConnexion

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée deux utilisateurs de test pour tester les suggestions de connexion'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Création de deux utilisateurs pour tester les suggestions...")
        
        # Créer le premier utilisateur
        user1 = self._create_user(
            email='alice@test.com',
            username='alice_test',
            first_name='Alice',
            last_name='Test',
            profession='Développeuse',
            passions=['programmation', 'lecture', 'voyage'],
            objectifs_personnels=['Apprendre Django', 'Voyager plus']
        )
        
        # Créer le deuxième utilisateur
        user2 = self._create_user(
            email='bob@test.com', 
            username='bob_test',
            first_name='Bob',
            last_name='Test',
            profession='Designer',
            passions=['design', 'art', 'musique'],
            objectifs_personnels=['Améliorer le design', 'Apprendre la musique']
        )
        
        # Créer des journaux de test pour les utilisateurs
        self._create_test_journals(user1, user2)
        
        # Créer des suggestions entre les deux utilisateurs
        self._create_suggestions(user1, user2)
        
        self.stdout.write(self.style.SUCCESS('🎉 Utilisateurs de test créés avec succès!'))
        self.stdout.write(f"👤 Alice: {user1.email} / motdepasse: testpass123")
        self.stdout.write(f"👤 Bob: {user2.email} / motdepasse: testpass123")
        self.stdout.write("\n📝 Instructions de test:")
        self.stdout.write("1. Connectez-vous avec Alice")
        self.stdout.write("2. Allez sur /communication/suggestions/")
        self.stdout.write("3. Acceptez la suggestion de Bob")
        self.stdout.write("4. Connectez-vous avec Bob")
        self.stdout.write("5. Vérifiez que la connexion est acceptée")

    def _create_user(self, email, username, first_name, last_name, profession, passions, objectifs_personnels):
        """Crée un utilisateur de test"""
        try:
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
                    'humeur_generale': 'heureux',
                    'niveau_stress': 2,
                    'qualite_sommeil': 'bon',
                    'frequence_ecriture_souhaitee': 'soir',
                    'moment_prefere_ecriture': 'soir',
                    'niveau_activite_physique': 'modere',
                    'habitudes_alimentaires': 'equilibree',
                    'heures_sommeil_par_nuit': 8.0,
                    'centres_interet': ['technologie', 'développement personnel'],
                    'preferences_suivi': {'notifications': True, 'rapports_automatiques': True}
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Utilisateur {username} créé'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Utilisateur {username} existe déjà'))
            
            return user
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création utilisateur {username}: {e}'))
            return None

    def _create_suggestions(self, user1, user2):
        """Crée des suggestions de connexion entre les deux utilisateurs"""
        try:
            # Suggestion de Alice vers Bob (proposée)
            suggestion1, created1 = SuggestionConnexion.objects.get_or_create(
                utilisateur_source=user1,
                utilisateur_cible=user2,
                defaults={
                    'score_similarite': 0.75,
                    'type_suggestion': 'objectif_similaire',
                    'statut': 'proposee',
                    'date_suggestion': timezone.now() - timedelta(days=1)
                }
            )
            
            if created1:
                self.stdout.write(self.style.SUCCESS('✅ Suggestion Alice → Bob créée (proposée)'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Suggestion Alice → Bob existe déjà'))
            
            # Suggestion de Bob vers Alice (proposée)
            suggestion2, created2 = SuggestionConnexion.objects.get_or_create(
                utilisateur_source=user2,
                utilisateur_cible=user1,
                defaults={
                    'score_similarite': 0.68,
                    'type_suggestion': 'interet_commun',
                    'statut': 'proposee',
                    'date_suggestion': timezone.now() - timedelta(hours=12)
                }
            )
            
            if created2:
                self.stdout.write(self.style.SUCCESS('✅ Suggestion Bob → Alice créée (proposée)'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Suggestion Bob → Alice existe déjà'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création suggestions: {e}'))

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
            
            self.stdout.write(self.style.SUCCESS('✅ Journaux de test créés pour Alice et Bob'))
            
        except ImportError:
            self.stdout.write(self.style.WARNING('⚠️ Modèle Journal non disponible'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur création journaux: {e}'))
