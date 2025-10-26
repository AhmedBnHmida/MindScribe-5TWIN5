from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communication.models import RapportPDF, HistoriqueGeneration

User = get_user_model()

class Command(BaseCommand):
    help = 'Nettoie les données de test PDF'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Nettoyage des données de test PDF...")
        
        # Supprimer l'utilisateur de test PDF
        deleted_count = User.objects.filter(email='test_pdf@mindscribe.com').delete()
        if deleted_count[0] > 0:
            self.stdout.write(self.style.SUCCESS('✅ Utilisateur de test PDF supprimé'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Aucun utilisateur de test PDF trouvé'))
        
        # Supprimer les rapports de test (au cas où)
        rapport_count = RapportPDF.objects.filter(utilisateur__email='test_pdf@mindscribe.com').delete()
        if rapport_count[0] > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ {rapport_count[0]} rapports de test supprimés'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Nettoyage terminé!'))