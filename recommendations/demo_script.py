"""
Demo script to test the Recommendations module.
Run with: python manage.py shell < recommendations/demo_script.py
"""

print("=" * 60)
print("🎉 DÉMONSTRATION MODULE RECOMMANDATIONS")
print("=" * 60)

from django.contrib.auth import get_user_model
from module2_analysis.models import JournalAnalysis
from recommendations.models import Recommandation, Objectif
from recommendations.services import create_recommendations_for_user, get_user_analysis_summary
from datetime import datetime, timedelta

User = get_user_model()

# Créer ou récupérer un utilisateur de test
user, created = User.objects.get_or_create(
    username='test_reco',
    defaults={
        'email': 'test@mindscribe.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)

if created:
    user.set_password('password123')
    user.save()
    print(f"\n✅ Utilisateur créé: {user.username}")
else:
    print(f"\n✅ Utilisateur existant: {user.username}")

# Créer des entrées de journal de test
print("\n📝 Création de 5 entrées de journal...")
sentiments = ['positif', 'neutre', 'negatif', 'positif', 'neutre']
scores = [0.8, 0.5, 0.3, 0.7, 0.6]
textes = [
    "Excellente journée de travail, j'ai accompli tous mes objectifs!",
    "Journée normale, rien de spécial à signaler.",
    "Je me sens fatigué et démotivé aujourd'hui.",
    "Belle promenade dans le parc, je me sens revigoré.",
    "Réunion productive avec l'équipe."
]

for i, (sentiment, score, texte) in enumerate(zip(sentiments, scores, textes)):
    analysis = JournalAnalysis.objects.create(
        user=user,
        text=texte,
        sentiment=sentiment,
        emotion_score=score,
        keywords=['travail', 'équipe', 'objectifs'],
        topics=['professionnel', 'bien-être'],
        summary=f"Résumé de l'entrée {i+1}"
    )
    print(f"  ✓ Entrée {i+1}: {sentiment} (score: {score})")

# Obtenir le résumé d'analyse
print("\n📊 Analyse des patterns...")
summary = get_user_analysis_summary(user, days=7)
print(f"  Total entrées: {summary['total_entries']}")
print(f"  Score émotionnel moyen: {summary['average_emotion_score']:.2f}")
print(f"  Distribution sentiments: {summary['sentiment_distribution']}")
print(f"  Tendance: {summary['trend']}")

# Générer des recommandations
print("\n🤖 Génération de recommandations IA...")
try:
    recommendations = create_recommendations_for_user(user)
    print(f"  ✅ {len(recommendations)} recommandations générées!")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n  {i}. [{rec.type.upper()}] {rec.contenu[:80]}...")
except Exception as e:
    print(f"  ⚠️  Erreur: {e}")
    print("  💡 Note: Vérifiez la clé API OpenRouter")

# Créer un objectif de test
print("\n🎯 Création d'un objectif...")
today = datetime.now().date()
objectif = Objectif.objects.create(
    utilisateur=user,
    nom="Méditer 10 minutes par jour",
    description="Pratiquer la méditation chaque matin pour améliorer ma concentration",
    progres=30.0,
    date_debut=today,
    date_fin=today + timedelta(days=30)
)
print(f"  ✅ Objectif créé: {objectif.nom}")
print(f"  Progrès actuel: {objectif.progres}%")
print(f"  Date fin: {objectif.date_fin}")

# Statistiques finales
print("\n📈 STATISTIQUES FINALES:")
total_recs = Recommandation.objects.filter(utilisateur=user).count()
total_objectifs = Objectif.objects.filter(utilisateur=user).count()
print(f"  Recommandations totales: {total_recs}")
print(f"  Objectifs actifs: {total_objectifs}")

print("\n" + "=" * 60)
print("✅ DÉMONSTRATION TERMINÉE!")
print("🌐 Accédez à: http://127.0.0.1:8000/recommendations/")
print("=" * 60)

