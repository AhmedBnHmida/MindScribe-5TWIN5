"""
Management command to clean up test suggestion data.
Removes test users and their suggestions for fresh testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communication.models import SuggestionConnexion

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up test users and suggestions for fresh testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users-only',
            action='store_true',
            help='Only clean test users, not suggestions',
        )
        parser.add_argument(
            '--suggestions-only',
            action='store_true',
            help='Only clean suggestions, not users',
        )
        parser.add_argument(
            '--all-test',
            action='store_true',
            help='Clean ALL test users (alice, bob, charlie, test_user_*)',
        )

    def handle(self, *args, **options):
        self.stdout.write("Cleaning test suggestion data...\n")
        
        # List of test user identifiers
        test_emails = [
            'alice@test.com',
            'bob@test.com',
            'charlie@test.com',
            'test_pdf@mindscribe.com'
        ]
        
        test_usernames = [
            'alice_test',
            'bob_test',
            'test_user_alice',
            'test_user_bob',
            'test_user_charlie',
            'testuser_pdf'
        ]
        
        # Clean suggestions first (before deleting users)
        if not options['users_only']:
            suggestions_deleted = 0
            
            if options['all_test']:
                # Delete all suggestions involving test users
                for email in test_emails:
                    try:
                        user = User.objects.get(email=email)
                        count = SuggestionConnexion.objects.filter(
                            utilisateur_source=user
                        ).delete()[0]
                        suggestions_deleted += count
                        count = SuggestionConnexion.objects.filter(
                            utilisateur_cible=user
                        ).delete()[0]
                        suggestions_deleted += count
                    except User.DoesNotExist:
                        pass
                
                # Also clean test_user_* users
                for username in test_usernames:
                    try:
                        user = User.objects.get(username=username)
                        count = SuggestionConnexion.objects.filter(
                            utilisateur_source=user
                        ).delete()[0]
                        suggestions_deleted += count
                        count = SuggestionConnexion.objects.filter(
                            utilisateur_cible=user
                        ).delete()[0]
                        suggestions_deleted += count
                    except User.DoesNotExist:
                        pass
            else:
                # Standard cleanup - alice and bob only
                for email in ['alice@test.com', 'bob@test.com']:
                    try:
                        user = User.objects.get(email=email)
                        count = SuggestionConnexion.objects.filter(
                            utilisateur_source=user
                        ).delete()[0]
                        suggestions_deleted += count
                        count = SuggestionConnexion.objects.filter(
                            utilisateur_cible=user
                        ).delete()[0]
                        suggestions_deleted += count
                    except User.DoesNotExist:
                        pass
            
            if suggestions_deleted > 0:
                self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {suggestions_deleted} suggestions'))
            else:
                self.stdout.write('[INFO] No suggestions to delete')
        
        # Clean users
        if not options['suggestions_only']:
            users_deleted = 0
            
            if options['all_test']:
                # Delete all test users
                for email in test_emails:
                    try:
                        user = User.objects.get(email=email)
                        user.delete()
                        users_deleted += 1
                        self.stdout.write(f'  Deleted user: {email}')
                    except User.DoesNotExist:
                        pass
                
                for username in test_usernames:
                    try:
                        user = User.objects.get(username=username)
                        if user.email not in test_emails:  # Avoid double deletion
                            user.delete()
                            users_deleted += 1
                            self.stdout.write(f'  Deleted user: {username}')
                    except User.DoesNotExist:
                        pass
            else:
                # Standard cleanup - alice and bob only
                for email in ['alice@test.com', 'bob@test.com']:
                    try:
                        user = User.objects.get(email=email)
                        user.delete()
                        users_deleted += 1
                        self.stdout.write(f'  Deleted user: {email}')
                    except User.DoesNotExist:
                        pass
            
            if users_deleted > 0:
                self.stdout.write(self.style.SUCCESS(f'\n[OK] Deleted {users_deleted} test users'))
            else:
                self.stdout.write('\n[INFO] No test users to delete')
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Cleanup completed!'))
        self.stdout.write('\n[INFO] You can now run: python manage.py create_two_users_test')

