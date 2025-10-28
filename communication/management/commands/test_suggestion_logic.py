"""
Management command to test the enhanced suggestion connection logic.
Creates test users with different profile attributes and generates suggestions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communication.models import SuggestionConnexion
from communication.services.suggestion_service import SuggestionConnexionService

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the enhanced suggestion connection logic with sample users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Enhanced Suggestion Logic...\n'))
        
        # Create or get test users with different profiles
        user1, created1 = User.objects.get_or_create(
            username='test_user_alice',
            defaults={
                'email': 'alice@test.com',
                'password': 'pbkdf2_sha256$320000$dummy$dummy=',
                'objectifs_personnels': ['Apprendre Python', 'Méditation quotidienne', 'Voyager plus'],
                'centres_interet': ['Programmation', 'Yoga', 'Lecture', 'Photographie'],
                'humeur_generale': 'heureux',
                'profession': 'Développeuse',
                'passions': ['Code', 'Yoga', 'Photographie']
            }
        )
        
        user2, created2 = User.objects.get_or_create(
            username='test_user_bob',
            defaults={
                'email': 'bob@test.com',
                'password': 'pbkdf2_sha256$320000$dummy$dummy=',
                'objectifs_personnels': ['Apprendre Python', 'Fitness', 'Lire plus'],
                'centres_interet': ['Programmation', 'Fitness', 'Lecture'],
                'humeur_generale': 'heureux',
                'profession': 'Développeur',
                'passions': ['Code', 'Fitness']
            }
        )
        
        user3, created3 = User.objects.get_or_create(
            username='test_user_charlie',
            defaults={
                'email': 'charlie@test.com',
                'password': 'pbkdf2_sha256$320000$dummy$dummy=',
                'objectifs_personnels': ['Perdre du poids', 'Arrêter de fumer'],
                'centres_interet': ['Cuisine', 'Cinéma'],
                'humeur_generale': 'anxieux',
                'profession': 'Designer',
                'passions': ['Art', 'Cinéma']
            }
        )
        
        if created1 or created2 or created3:
            self.stdout.write(self.style.SUCCESS('[OK] Test users created/retrieved'))
        
        self.stdout.write('\n[INFO] User Profiles:')
        self.stdout.write(f'  Alice: objectifs={user1.objectifs_personnels}, intérêts={user1.centres_interet}, humeur={user1.humeur_generale}')
        self.stdout.write(f'  Bob:   objectifs={user2.objectifs_personnels}, intérêts={user2.centres_interet}, humeur={user2.humeur_generale}')
        self.stdout.write(f'  Charlie: objectifs={user3.objectifs_personnels}, intérêts={user3.centres_interet}, humeur={user3.humeur_generale}')
        
        # Clean existing suggestions for these users
        SuggestionConnexion.objects.filter(
            utilisateur_source__in=[user1, user2, user3]
        ).delete()
        self.stdout.write('\n[INFO] Cleaned existing suggestions')
        
        # Test similarity calculations
        self.stdout.write('\n[INFO] Calculating Similarities:')
        
        # Alice vs Bob
        similarity_alice_bob = SuggestionConnexionService.calculate_similarity(user1, user2)
        self.stdout.write(f'\n  Alice <-> Bob:')
        self.stdout.write(f'    Overall Score: {similarity_alice_bob["overall_score"]:.2%}')
        self.stdout.write(f'    Type: {similarity_alice_bob["type"]}')
        self.stdout.write(f'    Detailed Scores:')
        for key, value in similarity_alice_bob["detailed_scores"].items():
            self.stdout.write(f'      {key}: {value:.2%}')
        
        # Alice vs Charlie
        similarity_alice_charlie = SuggestionConnexionService.calculate_similarity(user1, user3)
        self.stdout.write(f'\n  Alice <-> Charlie:')
        self.stdout.write(f'    Overall Score: {similarity_alice_charlie["overall_score"]:.2%}')
        self.stdout.write(f'    Type: {similarity_alice_charlie["type"]}')
        self.stdout.write(f'    Detailed Scores:')
        for key, value in similarity_alice_charlie["detailed_scores"].items():
            self.stdout.write(f'      {key}: {value:.2%}')
        
        # Check if we should generate suggestions
        if similarity_alice_bob['overall_score'] >= SuggestionConnexionService.MIN_SIMILARITY_SCORE:
            self.stdout.write(f'\n[OK] Alice <-> Bob score ({similarity_alice_bob["overall_score"]:.2%}) is above threshold ({SuggestionConnexionService.MIN_SIMILARITY_SCORE:.0%})')
            self.stdout.write('     -> This match would generate a suggestion!')
        else:
            self.stdout.write(f'\n[INFO] Alice <-> Bob score ({similarity_alice_bob["overall_score"]:.2%}) is below threshold ({SuggestionConnexionService.MIN_SIMILARITY_SCORE:.0%})')
        
        if similarity_alice_charlie['overall_score'] >= SuggestionConnexionService.MIN_SIMILARITY_SCORE:
            self.stdout.write(f'\n[OK] Alice <-> Charlie score ({similarity_alice_charlie["overall_score"]:.2%}) is above threshold ({SuggestionConnexionService.MIN_SIMILARITY_SCORE:.0%})')
        else:
            self.stdout.write(f'\n[INFO] Alice <-> Charlie score ({similarity_alice_charlie["overall_score"]:.2%}) is below threshold ({SuggestionConnexionService.MIN_SIMILARITY_SCORE:.0%})')
            self.stdout.write('     -> This match would NOT generate a suggestion.')
        
        # Try to actually create a suggestion manually for demonstration
        self.stdout.write('\n[INFO] Creating sample suggestion with calculated score...')
        try:
            # Clean existing first
            SuggestionConnexion.objects.filter(
                utilisateur_source=user1,
                utilisateur_cible=user2
            ).delete()
            
            # Create with real calculated score
            suggestion = SuggestionConnexion.objects.create(
                utilisateur_source=user1,
                utilisateur_cible=user2,
                score_similarite=similarity_alice_bob['overall_score'],
                type_suggestion=similarity_alice_bob['type'],
                statut='proposee'
            )
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] Created suggestion: Alice -> Bob '
                f'(score: {suggestion.score_similarite:.2%}, type: {suggestion.get_type_suggestion_display()})'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  [INFO] Could not create suggestion: {e}'))
        
        self.stdout.write('\n' + self.style.SUCCESS('[OK] Test completed successfully!'))
        self.stdout.write('\n[INFO] Clean up test data: python manage.py clean_test_suggestions')
        self.stdout.write('[INFO] Create fresh test users: python manage.py create_two_users_test')

