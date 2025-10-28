# Module 4 – Recommandations et Accompagnement Personnel

## 🎯 Vue d'ensemble

Ce module fournit un système de recommandations personnalisées basé sur l'IA pour accompagner les utilisateurs dans leur parcours de bien-être. Il analyse les entrées de journal et les patterns émotionnels pour générer des conseils adaptés.

## 🌟 Fonctionnalités principales

### 1. Génération de Recommandations IA
- Utilise OpenRouter API (même clé que module2_analysis)
- Analyse les 7 derniers jours d'entrées de journal
- Génère 5 recommandations dans 3 catégories:
  - 🧘‍♀️ **Bien-être**: Conseils pour la santé mentale et émotionnelle
  - 💻 **Productivité**: Suggestions pour l'organisation et l'efficacité
  - 😴 **Sommeil/Repos**: Recommandations pour le repos et la récupération

### 2. Système de Déclenchement Automatique
Recommandations automatiques générées quand:
- ✅ L'utilisateur a 3+ entrées dans les 7 derniers jours
- ✅ Pas de recommandations reçues depuis 2 jours
- ✅ Pattern émotionnel détecté:
  - Tendance négative (declining)
  - Score émotionnel bas (< 0.4)
  - Ratio élevé de sentiments négatifs (> 50%)
  - Jalon atteint (chaque 5ème entrée)

### 3. Suivi d'Objectifs Personnels
- Création d'objectifs SMART
- Suivi du progrès (0-100%)
- Notifications de rappel pour objectifs proches de l'échéance
- Messages de célébration pour objectifs près de la complétion

### 4. Système de Feedback
- Statuts: Nouvelle / Suivie / Ignorée
- Évaluation de l'utilité (oui/non)
- Note sur 5 étoiles
- Commentaires détaillés

### 5. Dashboard Analytique
- Statistiques globales (total conseils, taux de suivi)
- Aperçu des 7 derniers jours
- Objectifs actifs
- Analyses émotionnelles

## 📂 Structure du Module

```
recommendations/
├── models.py              # Modèles Recommandation & Objectif
├── services.py            # Service IA + logique métier
├── views.py               # Vues Django
├── urls.py                # Configuration des URLs
├── signals.py             # Déclencheurs automatiques
├── admin.py               # Interface d'administration
└── templates/
    └── recommendations/
        ├── dashboard.html        # Page principale
        ├── list.html             # Liste filtrée
        ├── goals.html            # Gestion des objectifs
        ├── create_goal.html      # Création d'objectif
        └── insights.html         # Analyses approfondies
```

## 🔧 Configuration

### OpenRouter API
Le module utilise la même clé API que `module2_analysis`:

```python
# Dans recommendations/services.py
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
```

### Modèle IA Utilisé
- **Modèle principal**: `mistralai/mistral-7b-instruct`
- **Température**: 0.7 (équilibre créativité/cohérence)
- **Max tokens**: 1000

## 🚀 Utilisation

### URLs Disponibles

```python
# Dashboard principal
/recommendations/

# Liste des recommandations (avec filtres)
/recommendations/list/?type=bien_etre&status=nouvelle

# Génération manuelle de recommandations
POST /recommendations/generate/

# Mise à jour du statut d'une recommandation
POST /recommendations/<uuid>/status/

# Gestion des objectifs
/recommendations/goals/
/recommendations/goals/create/
POST /recommendations/goals/<uuid>/progress/
POST /recommendations/goals/<uuid>/delete/

# Analyses et insights
/recommendations/insights/
```

### Utilisation Programmatique

```python
from recommendations.services import (
    create_recommendations_for_user,
    get_user_analysis_summary,
    mark_recommendation_status
)

# Générer des recommandations pour un utilisateur
recommendations = create_recommendations_for_user(user)

# Obtenir le résumé d'analyse
summary = get_user_analysis_summary(user, days=7)

# Marquer une recommandation comme suivie
mark_recommendation_status(recommendation_id, 'suivie')
```

## 🔔 Signals Django

### Déclenchement automatique
```python
# Signal: post_save sur JournalAnalysis
# Déclenche automatiquement des recommandations selon les conditions
```

### Vérification des objectifs
```python
# Fonction appelable par Celery pour vérifier les objectifs
from recommendations.signals import check_user_goals_progress
check_user_goals_progress(user)
```

## 📊 Modèles de Données

### Recommandation
```python
- id (UUID)
- utilisateur (ForeignKey → User)
- type (bien_etre / productivite / sommeil / nutrition)
- contenu (TextField)
- statut (nouvelle / suivie / ignoree)
- date_emission (DateTimeField)
- utile (BooleanField, nullable)
- feedback_note (IntegerField 1-5, nullable)
- feedback_commentaire (TextField)
```

### Objectif
```python
- id (UUID)
- utilisateur (ForeignKey → User)
- nom (CharField)
- description (TextField)
- progres (FloatField 0-100)
- date_debut (DateField)
- date_fin (DateField)
- date_creation (DateTimeField)
- date_mise_a_jour (DateTimeField)
```

## 🎨 Interface Utilisateur

### Design System
- Style **ultra-modern** cohérent avec le reste de l'app
- **Glass-morphism** cards
- **Gradient backgrounds** pour les badges
- **Animations** smooth sur hover
- **Responsive** design (Bootstrap 5)

### Couleurs par Catégorie
- 💜 **Bien-être**: Gradient violet/rose
- 🌸 **Productivité**: Gradient rose/rouge
- 💙 **Sommeil**: Gradient bleu clair
- 💚 **Nutrition**: Gradient vert

## 🧪 Tests

Pour tester le module:

```bash
# 1. Créer une entrée de journal
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from module2_analysis.models import JournalAnalysis
>>> user = get_user_model().objects.first()
>>> for i in range(5):
...     JournalAnalysis.objects.create(
...         user=user,
...         text=f"Test entry {i}",
...         sentiment='neutre',
...         emotion_score=0.5
...     )

# 2. Les recommandations seront générées automatiquement via signal
# OU générer manuellement:
>>> from recommendations.services import create_recommendations_for_user
>>> recs = create_recommendations_for_user(user)
>>> print(f"Generated {len(recs)} recommendations")
```

## 📈 Métriques & KPIs

Le système track:
- Nombre total de recommandations générées
- Taux de suivi (suivies / total)
- Répartition par type
- Taux de complétion des objectifs
- Score d'amélioration émotionnelle

## 🔮 Améliorations Futures

1. **Notifications Push** (via Django Channels / Firebase)
2. **Scheduler Celery** pour génération quotidienne
3. **Machine Learning** pour personnalisation avancée
4. **Gamification** (badges, streaks, points)
5. **Intégration Calendrier** pour objectifs
6. **Export PDF** des rapports de progrès

## 🤝 Intégration avec les Autres Modules

### Module 2 (Analysis)
- Lit les données de `JournalAnalysis`
- Utilise les métriques de sentiment, émotions, keywords

### Module Dashboard
- Peut afficher des widgets de recommandations
- Statistiques intégrées

### Module Communication
- Partage la configuration OpenRouter
- Peut suggérer des conversations avec l'assistant IA

## 📝 Notes de Développement

- **Framework**: Django 3.2.21
- **Database**: MongoDB (via Djongo)
- **AI Provider**: OpenRouter (Mistral AI)
- **Frontend**: Bootstrap 5 + Vanilla JS
- **Charts**: Chart.js 3.9.1

## 🐛 Dépannage

### Recommandations ne se génèrent pas
- Vérifier que l'utilisateur a au moins 3 entrées de journal
- Vérifier la clé API OpenRouter
- Consulter les logs: `logger.info` dans `services.py`

### Erreur Unicode
- Assurez-vous que le fichier utilise UTF-8
- Windows: Peut nécessiter `chcp 65001` dans le terminal

### Migrations
```bash
python manage.py makemigrations recommendations
python manage.py migrate recommendations
```

## 📞 Support

Pour toute question ou problème, consultez:
- Documentation Django: https://docs.djangoproject.com
- OpenRouter API: https://openrouter.ai/docs
- Logs de l'application: Voir les prints de debug

---

**Version**: 1.0.0
**Auteur**: MindScribe Development Team
**Date**: Octobre 2025

