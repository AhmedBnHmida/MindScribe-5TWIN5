from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from communication.models import SuggestionConnexion

User = get_user_model()

class Command(BaseCommand):
    help = 'Nettoie les deux utilisateurs de test pour les suggestions'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Nettoyage des deux utilisateurs de test...")
        
        # Supprimer les suggestions entre les deux utilisateurs (une par une pour éviter les erreurs MongoDB)
        suggestions_count = 0
        
        # Supprimer les suggestions où Alice est source
        alice_source_suggestions = SuggestionConnexion.objects.filter(utilisateur_source__email='alice@test.com')
        for suggestion in alice_source_suggestions:
            suggestion.delete()
            suggestions_count += 1
        
        # Supprimer les suggestions où Alice est cible
        alice_target_suggestions = SuggestionConnexion.objects.filter(utilisateur_cible__email='alice@test.com')
        for suggestion in alice_target_suggestions:
            suggestion.delete()
            suggestions_count += 1
        
        # Supprimer les suggestions où Bob est source
        bob_source_suggestions = SuggestionConnexion.objects.filter(utilisateur_source__email='bob@test.com')
        for suggestion in bob_source_suggestions:
            suggestion.delete()
            suggestions_count += 1
        
        # Supprimer les suggestions où Bob est cible
        bob_target_suggestions = SuggestionConnexion.objects.filter(utilisateur_cible__email='bob@test.com')
        for suggestion in bob_target_suggestions:
            suggestion.delete()
            suggestions_count += 1
        
        if suggestions_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ {suggestions_count} suggestions supprimées'))
        
        # Supprimer les utilisateurs (un par un pour éviter les erreurs MongoDB)
        deleted_users = 0
        
        # Supprimer Alice
        try:
            alice = User.objects.get(email='alice@test.com')
            alice.delete()
            deleted_users += 1
            self.stdout.write(self.style.SUCCESS('✅ Alice supprimée'))
        except User.DoesNotExist:
            pass
        
        # Supprimer Bob
        try:
            bob = User.objects.get(email='bob@test.com')
            bob.delete()
            deleted_users += 1
            self.stdout.write(self.style.SUCCESS('✅ Bob supprimé'))
        except User.DoesNotExist:
            pass
        
        if deleted_users == 0:
            self.stdout.write(self.style.WARNING('⚠️ Aucun utilisateur de test trouvé'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Nettoyage terminé!'))
