from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Imports conditionnels
try:
    from journal.models import Journal
except ImportError:
    Journal = None

try:
    from dashboard.models import Statistique
except ImportError:
    Statistique = None

class Command(BaseCommand):
    help = 'Cree uniquement les utilisateurs de test (Alice, Bob, Charlie) pour tester les fonctionnalites manuellement'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("[START] CREATION DES UTILISATEURS DE TEST"))
        self.stdout.write("=" * 70)
        
        # Créer les 3 utilisateurs de test
        alice = self._create_user_alice()
        bob = self._create_user_bob()
        charlie = self._create_user_charlie()
        
        if not alice or not bob or not charlie:
            self.stdout.write(self.style.ERROR('[ERROR] Echec de la creation des utilisateurs'))
            return
        
        # Créer des journaux pour chaque utilisateur
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("[INFO] CREATION DES JOURNAUX")
        self.stdout.write("=" * 70)
        self._create_journals_for_users([alice, bob, charlie])
        
        # Créer des statistiques pour chaque utilisateur
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("[INFO] CREATION DES STATISTIQUES")
        self.stdout.write("=" * 70)
        self._create_statistics([alice, bob, charlie])
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("[OK] UTILISATEURS CREES AVEC SUCCES !"))
        self.stdout.write("=" * 70)
        self.stdout.write("\n[INFO] CREDENTIALS DE CONNEXION:")
        self.stdout.write(f"   Alice:   {alice.email} / testpass123")
        self.stdout.write(f"   Bob:     {bob.email} / testpass123")
        self.stdout.write(f"   Charlie: {charlie.email} / testpass123")
        self.stdout.write("\n[INFO] Vous pouvez maintenant tester:")
        self.stdout.write("   - Generation de suggestions: /communication/suggestions/generer/")
        self.stdout.write("   - Generation PDF: /communication/rapports/generer/")
        self.stdout.write("   - Conversations IA: /communication/assistant-ia/")

    def _create_user_alice(self):
        """Crée l'utilisateur Alice (Développeuse, heureuse, interêts tech)"""
        user, created = User.objects.get_or_create(
            email='alice@test.com',
            defaults={
                'username': 'alice_test',
                'first_name': 'Alice',
                'last_name': 'Developer',
                'is_active': True,
                'role': 'user',
                'profession': 'Développeuse Full-Stack',
                'passions': ['programmation', 'lecture', 'yoga', 'voyage'],
                'objectifs_personnels': ['Apprendre Django avancé', 'Méditation quotidienne', 'Améliorer mes compétences', 'Lire plus'],
                'centres_interet': ['Programmation', 'Yoga', 'Lecture', 'Développement personnel', 'Technologie'],
                'humeur_generale': 'heureux',
                'niveau_stress': 2,
                'qualite_sommeil': 'bon',
                'age': 28,
                'langue': 'fr',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('[OK] Alice creee (Developpeuse, heureuse, tech)'))
        else:
            self.stdout.write(self.style.WARNING('[WARN] Alice existe deja'))
        return user

    def _create_user_bob(self):
        """Crée l'utilisateur Bob (Développeur, heureux, interêts tech)"""
        user, created = User.objects.get_or_create(
            email='bob@test.com',
            defaults={
                'username': 'bob_test',
                'first_name': 'Bob',
                'last_name': 'Designer',
                'is_active': True,
                'role': 'user',
                'profession': 'Développeur Frontend',
                'passions': ['code', 'fitness', 'lecture', 'design'],
                'objectifs_personnels': ['Apprendre React', 'Améliorer mes compétences', 'Lire plus', 'Développement personnel'],
                'centres_interet': ['Programmation', 'Fitness', 'Lecture', 'Design', 'Technologie'],
                'humeur_generale': 'heureux',
                'niveau_stress': 3,
                'qualite_sommeil': 'bon',
                'age': 30,
                'langue': 'fr',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('[OK] Bob cree (Developpeur, heureux, tech)'))
        else:
            self.stdout.write(self.style.WARNING('[WARN] Bob existe deja'))
        return user

    def _create_user_charlie(self):
        """Crée l'utilisateur Charlie (Artiste, anxieux, interêts créatifs)"""
        user, created = User.objects.get_or_create(
            email='charlie@test.com',
            defaults={
                'username': 'charlie_test',
                'first_name': 'Charlie',
                'last_name': 'Artist',
                'is_active': True,
                'role': 'user',
                'profession': 'Artiste indépendant',
                'passions': ['peinture', 'musique', 'photographie'],
                'objectifs_personnels': ['Exposition de mes œuvres', 'Vivre de mon art'],
                'centres_interet': ['Art', 'Musique', 'Photographie', 'Créativité'],
                'humeur_generale': 'anxieux',
                'niveau_stress': 6,
                'qualite_sommeil': 'moyen',
                'age': 25,
                'langue': 'fr',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('[OK] Charlie cree (Artiste, anxieux, creatif)'))
        else:
            self.stdout.write(self.style.WARNING('[WARN] Charlie existe deja'))
        return user

    def _create_journals_for_users(self, users):
        """Crée des journaux variés pour chaque utilisateur"""
        if not Journal:
            self.stdout.write(self.style.WARNING('[WARN] Modele Journal non disponible'))
            return
        
        journals_data = {
            'alice': [
                "Aujourd'hui j'ai terminé mon projet Django. Je me sens très satisfaite du résultat et j'ai appris beaucoup de nouvelles choses sur les modèles et les vues.",
                "Journée productive au travail. J'ai résolu plusieurs bugs complexes et l'équipe était contente de mes contributions. Je me sens motivée pour continuer.",
                "Super journée ! J'ai fait du sport le matin, puis j'ai lu un livre fascinant sur la programmation. L'équilibre travail-loisirs est important pour moi.",
                "Réflexion du jour : j'ai remarqué que ma productivité est meilleure quand je commence par une petite marche. Je vais essayer de maintenir cette routine.",
                "Un peu stressée aujourd'hui avec plusieurs deadlines, mais j'ai réussi à tout gérer. Une bonne nuit de sommeil m'aidera à récupérer."
            ],
            'bob': [
                "Nouveau projet de design en cours. J'adore créer des interfaces utilisateur intuitives et belles. L'art et la technologie se rencontrent parfaitement.",
                "Journée créative ! J'ai travaillé sur une nouvelle palette de couleurs et j'ai été inspiré par l'art moderne. La créativité coule naturellement aujourd'hui.",
                "Écoute de musique classique en travaillant. Ça m'aide à me concentrer et à être plus créatif. La musique est vraiment une source d'inspiration.",
                "Réflexion sur mon parcours de développeur. J'ai parcouru un long chemin et je suis fier de mes réalisations. L'apprentissage continu est la clé.",
                "Séance de fitness ce matin. Je me sens énergique et prêt pour la journée. L'exercice est vraiment essentiel pour mon bien-être mental."
            ],
            'charlie': [
                "J'ai terminé ma nouvelle série de peintures. Je suis satisfait du résultat mais j'ai un peu d'anxiété concernant l'exposition à venir.",
                "Journée difficile. Je me suis senti bloqué créativement. J'espère que demain sera meilleur. La pression de créer quelque chose de nouveau peut être lourde.",
                "Écoute de jazz en travaillant sur mes projets. La musique me calme et m'inspire. J'ai découvert de nouveaux artistes aujourd'hui.",
                "Visite d'une galerie d'art. Ça m'a redonné de l'inspiration et m'a rappelé pourquoi j'aime ce que je fais. Malgré les doutes, je continue.",
                "Petit moment de réflexion. Parfois je me demande si j'ai pris la bonne direction. Mais l'art est ma passion et je dois continuer."
            ]
        }
        
        user_names = ['alice', 'bob', 'charlie']
        for idx, user in enumerate(users):
            if idx < len(user_names):
                journals = journals_data.get(user_names[idx], [])
                created_count = 0
                for i, content in enumerate(journals):
                    # Check if journal already exists for this user with this content
                    existing = Journal.objects.filter(
                        utilisateur=user,
                        contenu_texte=content
                    ).first()
                    
                    if not existing:
                        Journal.objects.create(
                            utilisateur=user,
                            contenu_texte=content,
                            type_entree='texte',
                            categorie='réflexion',
                            date_creation=timezone.now() - timedelta(days=len(journals)-i)
                        )
                        created_count += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] {created_count}/{len(journals)} journaux crees pour {user.first_name}'))

    def _create_statistics(self, users):
        """Crée des statistiques mensuelles pour chaque utilisateur"""
        if not Statistique:
            self.stdout.write(self.style.WARNING('[WARN] Modele Statistique non disponible'))
            return
        
        for user in users:
            periode = timezone.now().strftime('%B %Y')
            stat, created = Statistique.objects.get_or_create(
                utilisateur=user,
                periode=periode,
                defaults={
                    'frequence_ecriture': 15,
                    'score_humeur': 7.5 if user.humeur_generale == 'heureux' else 5.0,
                    'themes_dominants': ['travail', 'bien-être', 'développement personnel'],
                    'bilan_mensuel': f'Mois de {periode} avec une bonne progression personnelle.'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Statistiques creees pour {user.first_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'[WARN] Statistiques existent deja pour {user.first_name}'))

