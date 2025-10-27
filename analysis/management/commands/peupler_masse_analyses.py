# analysis/management/commands/peupler_masse_analyses.py
from django.core.management.base import BaseCommand
from analysis.models import AnalyseIA
from journal.models import Journal
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import random
from django.db import models
from collections import Counter

class Command(BaseCommand):
    help = 'Peuple la base avec une masse de données AnalyseIA diversifiées pour testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nb_journaux',
            type=int,
            default=100,
            help='Nombre de journaux à créer (défaut: 100)'
        )
        parser.add_argument(
            '--utilisateur',
            type=str,
            help="Email de l'utilisateur cible"
        )

    def handle(self, *args, **options):
        nb_journaux = options['nb_journaux']
        
        # Récupère ou crée l'utilisateur
        User = get_user_model()
        if options['utilisateur']:
            user = User.objects.get(email=options['utilisateur'])
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write("Création d'un utilisateur de test...")
                user = User.objects.create_user(
                    username='testeur',
                    email='test@mindsribe.com',
                    password='test123',
                    age=30,
                    profession='Développeur',
                    passions=['informatique', 'sport', 'lecture']
                )
        
        self.stdout.write(f"Utilisation de l'utilisateur: {user.username}")

        # Données de configuration très diversifiées
        THEMES_POSSIBLES = [
            'travail', 'famille', 'santé', 'loisirs', 'projets', 'relations', 
            'voyage', 'apprentissage', 'sport', 'culture', 'technologie',
            'nature', 'créativité', 'développement personnel', 'finance',
            'cuisine', 'musique', 'art', 'écriture', 'méditation'
        ]

        MOTS_CLES_PAR_CATEGORIE = {
            'travail': ['réunion', 'délai', 'collègue', 'projet', 'présentation', 'deadline', 'bureau'],
            'famille': ['enfant', 'parent', 'repas', 'discussion', 'soutien', 'fête', 'tradition'],
            'santé': ['exercice', 'médecin', 'récupération', 'bien-être', 'nutrition', 'sommeil', 'énergie'],
            'loisirs': ['film', 'lecture', 'jeu', 'promenade', 'restaurant', 'concert', 'détente'],
            'projets': ['planification', 'objectif', 'progrès', 'challenge', 'réalisation', 'innovation'],
            'voyage': ['destination', 'aventure', 'découverte', 'culture', 'souvenir', 'exploration'],
            'apprentissage': ['cours', 'compétence', 'connaissance', 'découverte', 'étude', 'maîtrise'],
            'sport': ['entraînement', 'performance', 'endurance', 'victoire', 'défaite', 'équipe'],
        }

        # Patterns d'évolution d'humeur réalistes
        def generer_pattern_humeur(index, total):
            """Génère des patterns d'humeur réalistes sur la période"""
            # Pattern cyclique (humeur qui varie sur la période)
            cycle = (index % 21) / 20.0  # Cycle de 3 semaines
            
            if cycle < 0.3:
                return 'positif'
            elif cycle < 0.6:
                return 'neutre'
            else:
                return 'negatif'

        # Création des journaux et analyses
        self.stdout.write(f"Création de {nb_journaux} journaux et analyses...")
        
        analyses_creees = 0
        date_base = datetime.now() - timedelta(days=nb_journaux)

        for i in range(nb_journaux):
            try:
                # Date progressive (du passé vers aujourd'hui)
                date_journal = date_base + timedelta(days=i)
                
                # Détermine le ton selon un pattern réaliste
                ton = generer_pattern_humeur(i, nb_journaux)
                
                # Sélectionne 2-4 thèmes cohérents
                nb_themes = random.randint(2, 4)
                themes = random.sample(THEMES_POSSIBLES, nb_themes)
                
                # Génère des mots-clés basés sur les thèmes
                mots_cles = []
                for theme in themes:
                    if theme in MOTS_CLES_PAR_CATEGORIE:
                        mots_cles.extend(random.sample(MOTS_CLES_PAR_CATEGORIE[theme], 2))
                
                # Élimine les doublons
                mots_cles = list(set(mots_cles))[:8]  # Maximum 8 mots-clés
                
                # Crée le contenu du journal réaliste
                contenu_texte = self.generer_contenu_journal(ton, themes, mots_cles, date_journal)
                
                # Crée le journal
                journal = Journal.objects.create(
                    utilisateur=user,
                    contenu_texte=contenu_texte,
                    type_entree=random.choice(['texte', 'texte', 'texte', 'audio', 'image']),  # Majorité texte
                    date_creation=date_journal,
                    categorie=random.choice(['quotidien', 'réflexion', 'projet', 'personnel', ''] + themes[:1])
                )
                
                # Génère le résumé IA réaliste
                resume = self.generer_resume_ia(ton, themes, mots_cles, date_journal)
                
                # Crée l'analyse IA
                AnalyseIA.objects.create(
                    journal=journal,
                    mots_cles=mots_cles,
                    ton_general=ton,
                    themes_detectes=themes,
                    resume_journee=resume
                )
                
                analyses_creees += 1
                
                if analyses_creees % 20 == 0:
                    self.stdout.write(f"{analyses_creees} analyses créées...")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur sur l'itération {i}: {e}"))
                continue

        # Crée quelques patterns spécifiques pour les tests
        self.creer_patterns_specifiques(user)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Peuplement terminé! {analyses_creees} analyses créées avec des données diversifiées'
            )
        )
        
        # Affiche quelques statistiques
        self.afficher_statistiques(user)

    def generer_contenu_journal(self, ton, themes, mots_cles, date):
        """Génère un contenu de journal réaliste en français"""
        
        introductions = {
            'positif': [
                "Quelle journée incroyable ! ",
                "Je me sens vraiment bien aujourd'hui. ",
                "Journée remplie de belles surprises. ",
                "Quel bonheur de constater mes progrès. "
            ],
            'neutre': [
                "Aujourd'hui s'est déroulé comme prévu. ",
                "Journée assez standard dans l'ensemble. ",
                "Rien de particulièrement marquant aujourd'hui. ",
                "Une journée comme les autres. "
            ],
            'negatif': [
                "Journée difficile aujourd'hui. ",
                "Je me sens un peu perdu en ce moment. ",
                "Pas facile de garder le moral aujourd'hui. ",
                "Une journée pleine de défis. "
            ]
        }
        
        phrases_suites = [
            f"J'ai principalement travaillé sur {', '.join(themes[:2])}. ",
            f"Mes réflexions tournaient autour de {random.choice(themes)}. ",
            f"L'aspect {random.choice(themes)} a particulièrement retenu mon attention. ",
            f"J'ai consacré du temps à développer mes compétences en {random.choice(themes)}. "
        ]
        
        conclusions = {
            'positif': [
                "Je me couche avec le sourire et plein d'enthousiasme pour demain.",
                "Quel sentiment gratifiant de voir les efforts porter leurs fruits !",
                "Cette journée m'a redonné confiance et motivation.",
                "Je me sens reconnaissant pour toutes ces belles expériences."
            ],
            'neutre': [
                "Demain sera un autre jour, avec ses propres défis et opportunités.",
                "Je vais me reposer et attaquer demain avec fraîcheur.",
                "La routine a du bon, elle apporte une certaine stabilité.",
                "Journée correcte dans l'ensemble, sans grands bouleversements."
            ],
            'negatif': [
                "J'espère que demain apportera plus de clarté et de sérénité.",
                "Il faut que je trouve un moyen de surmonter ces difficultés.",
                "Une bonne nuit de sommeil me fera sûrement du bien.",
                "Je dois apprendre à gérer ce genre de situations différemment."
            ]
        }
        
        contenu = (
            random.choice(introductions[ton]) +
            random.choice(phrases_suites) +
            f"Les mots qui me viennent à l'esprit sont : {', '.join(mots_cles[:3])}. " +
            random.choice(conclusions[ton])
        )
        
        return contenu

    def generer_resume_ia(self, ton, themes, mots_cles, date):
        """Génère un résumé IA réaliste"""
        
        templates_resume = {
            'positif': [
                f"Journée très positive marquée par {', '.join(themes)}. L'utilisateur montre un engagement remarquable et une énergie constructive. Sentiment général d'accomplissement et de progression.",
                f"Excellente journée avec une focalisation sur {random.choice(themes)}. Humeur optimiste et proactive. Les indicateurs émotionnels sont tous au vert avec une motivation palpable.",
                f"Performance émotionnelle élevée aujourd'hui. L'utilisateur a brillamment géré les aspects {', '.join(themes[:2])}. Très bon équilibre entre productivité et bien-être."
            ],
            'neutre': [
                f"Journée équilibrée avec une attention sur {', '.join(themes)}. Stabilité émotionnelle notable, bonne gestion des tâches courantes sans pic particulier.",
                f"Routine productive maintenue. L'utilisateur a avancé sur {random.choice(themes)} de manière constante. État d'esprit pragmatique et réaliste.",
                f"Transition douce entre les différentes activités. Focus sur {', '.join(themes)} sans tension particulière. Gestion efficace du temps et des priorités."
            ],
            'negatif': [
                f"Journée challenging avec des difficultés dans le domaine {random.choice(themes)}. L'utilisateur semble rencontrer certains obstacles nécessitant une attention particulière.",
                f"Période de réflexion intense sur {', '.join(themes)}. Quelques tensions perceptibles dans la gestion des émotions. Besoin de soutien identifié.",
                f"Ressources émotionnelles mises à l'épreuve aujourd'hui. Les défis liés à {random.choice(themes)} ont impacté l'humeur générale. Période de recalibrage nécessaire."
            ]
        }
        
        return random.choice(templates_resume[ton])

    def creer_patterns_specifiques(self, user):
        """Crée des patterns spécifiques pour tester les visualisations"""
        
        self.stdout.write("Création de patterns spécifiques...")
        
        # Pattern 1: Semaine très positive
        date_debut = datetime.now() - timedelta(days=14)
        for i in range(7):
            date_journal = date_debut + timedelta(days=i)
            journal = Journal.objects.create(
                utilisateur=user,
                contenu_texte=f"Semaine positive jour {i+1} - Progrès exceptionnels sur tous mes projets !",
                date_creation=date_journal
            )
            AnalyseIA.objects.create(
                journal=journal,
                mots_cles=['succès', 'progrès', 'réalisation', 'fierté', 'accomplissement'],
                ton_general='positif',
                themes_detectes=['projets', 'croissance', 'développement'],
                resume_journee=f"Période exceptionnellement positive. Progression remarquable sur tous les fronts avec une énergie et une motivation au maximum."
            )

        # Pattern 2: Période de stress
        date_debut = datetime.now() - timedelta(days=21)
        for i in range(5):
            date_journal = date_debut + timedelta(days=i)
            journal = Journal.objects.create(
                utilisateur=user,
                contenu_texte=f"Période stressante jour {i+1} - Beaucoup de pression et de délais serrés.",
                date_creation=date_journal
            )
            AnalyseIA.objects.create(
                journal=journal,
                mots_cles=['stress', 'délai', 'pression', 'urgence', 'défi'],
                ton_general='negatif',
                themes_detectes=['travail', 'délais', 'responsabilités'],
                resume_journee="Période de tension avec des défis importants à relever. Gestion du stress nécessaire."
            )

    def afficher_statistiques(self, user):
        """Affiche des statistiques sur les données créées - VERSION CORRIGÉE"""
        
        analyses = AnalyseIA.objects.filter(journal__utilisateur=user)
        total = analyses.count()
        
        if total > 0:
            # CORRECTION : Utiliser values avec annotation correcte
            from django.db.models import Count
            
            stats_ton = analyses.values('ton_general').annotate(
                count=Count('id')
            ).order_by('ton_general')
            
            self.stdout.write("\n📊 STATISTIQUES DES DONNÉES CRÉÉES:")
            self.stdout.write(f"Total des analyses: {total}")
            
            for stat in stats_ton:
                pourcentage = (stat['count'] / total) * 100
                self.stdout.write(f"- {stat['ton_general']}: {stat['count']} ({pourcentage:.1f}%)")
            
            # Thèmes les plus fréquents
            tous_themes = []
            for analyse in analyses:
                tous_themes.extend(analyse.themes_detectes)
            
            themes_frequents = Counter(tous_themes).most_common(10)
            self.stdout.write("\n🎯 THÈMES DOMINANTS (Top 10):")
            for theme, count in themes_frequents:
                pourcentage_theme = (count / len(tous_themes)) * 100
                self.stdout.write(f"- {theme}: {count} occurrences ({pourcentage_theme:.1f}%)")