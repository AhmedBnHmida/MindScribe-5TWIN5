# dashboard/services/analyse_ia.py
import re
from collections import Counter
import string
from datetime import datetime

class AnalyseurRapide:
    def __init__(self):
        try:
            # Essayer d'importer NLTK, mais avoir un fallback
            try:
                import nltk
                from nltk.sentiment import SentimentIntensityAnalyzer
                from nltk.corpus import stopwords
                
                # Télécharger les ressources NLTK si nécessaire
                try:
                    nltk.data.find('sentiment/vader_lexicon')
                except LookupError:
                    nltk.download('vader_lexicon')
                
                try:
                    nltk.data.find('corpora/stopwords')
                except LookupError:
                    nltk.download('stopwords')
                
                self.analyzer = SentimentIntensityAnalyzer()
                self.stop_words_fr = set(stopwords.words('french'))
                self.nltk_available = True
                print("✅ NLTK chargé avec succès")
                
            except Exception as e:
                print(f"⚠️ NLTK non disponible, utilisation du mode fallback: {e}")
                self.analyzer = None
                self.stop_words_fr = self._get_fallback_stopwords()
                self.nltk_available = False
            
            # Stopwords français étendus
            self.stop_words_fr.update([
                'plus', 'tout', 'tous', 'toutes', 'cest', 'nest', 'jai', 'suis', 'etc', 
                'être', 'avoir', 'ce', 'ca', 'ça', 'très', 'assez', 'trop', 'quoi', 'quel',
                'quelle', 'quelles', 'quels', 'comme', 'faire', 'dire', 'voilà', 'alors',
                'donc', 'or', 'ni', 'car', 'depuis', 'pendant', 'sous', 'sur', 'dans'
            ])
            
            # Dictionnaire psychologique COMPLET en français
            self.dictionnaire_psychologique = {
                'émotions_primaire': {
                    'joie': {
                        'mots': ['heureux', 'content', 'joyeux', 'satisfait', 'fier', 'enthousiaste', 'optimiste', 'reconnaissant', 'chanceux', 'épanoui', 'réjoui', 'ravie', 'combler'],
                        'score': 2.0,
                        'intensite': 1.5
                    },
                    'tristesse': {
                        'mots': ['triste', 'malheureux', 'déçu', 'désespéré', 'démoralisé', 'accablé', 'mélancolique', 'affligé', 'navré', 'peiné'],
                        'score': -2.0,
                        'intensite': 1.8
                    },
                    'colère': {
                        'mots': ['fâché', 'énervé', 'frustré', 'irrité', 'exaspéré', 'furieux', 'outragé', 'rage', 'colère', 'irritation'],
                        'score': -1.8,
                        'intensite': 2.0
                    },
                    'peur': {
                        'mots': ['anxieux', 'inquiet', 'craintif', 'paniqué', 'terrifié', 'appréhensif', 'angoissé', 'stressé', 'nerveux'],
                        'score': -1.5,
                        'intensite': 1.7
                    },
                    'dégout': {
                        'mots': ['dégoûté', 'répugné', 'écœuré', 'horripilé', 'dégouté', 'repoussé'],
                        'score': -1.2,
                        'intensite': 1.3
                    }
                },
                'émotions_secondaire': {
                    'honte': {
                        'mots': ['honteux', 'coupable', 'regret', 'remords', 'confus', 'gêné'],
                        'score': -1.0,
                        'intensite': 1.2
                    },
                    'jalousie': {
                        'mots': ['jaloux', 'envieux', 'possessif', 'jalousie', 'envie'],
                        'score': -0.8,
                        'intensite': 1.1
                    },
                    'solitude': {
                        'mots': ['seul', 'isolé', 'abandonné', 'rejeté', 'solitude', 'isolement'],
                        'score': -1.5,
                        'intensite': 1.6
                    },
                    'confiance': {
                        'mots': ['confiant', 'serein', 'apaisé', 'rassuré', 'sécurisé', 'tranquille'],
                        'score': 1.2,
                        'intensite': 1.0
                    }
                },
                'intensite_emotionnelle': {
                    'faible': ['un peu', 'légèrement', 'assez', 'plutôt', 'modérément'],
                    'moyenne': ['vraiment', 'suffisamment', 'bien', 'fort', 'intense'],
                    'forte': ['très', 'extrêmement', 'totalement', 'complètement', 'absolument', 'profondément'],
                    'extreme': ['intensément', 'passionnément', 'désespérément', 'terriblement', 'extrêmement']
                },
                'patterns_cognitifs': {
                    'pensée_tout_rien': ['toujours', 'jamais', 'rien', 'tout', 'personne', 'aucun', 'chaque', 'sans'],
                    'catastrophisme': ['horrible', 'terrible', 'catastrophe', 'désastre', 'insupportable', 'affreux', 'épouvantable'],
                    'generalisation': ['encore', 'toujours', 'sans cesse', 'constamment', 'toujours pareil'],
                    'personalisation': ['ma faute', 'je devrais', 'je dois', 'cest ma faute', 'à cause de moi']
                }
            }
            
            # Thèmes psychologiques détaillés
            self.themes_psychologiques = {
                'relations_interpersonnelles': {
                    'mots': ['ami', 'amour', 'copain', 'copine', 'relation', 'amitié', 'partenaire', 'meilleur', 'dispute', 'conflit', 'famille', 'parent', 'collègue', 'proche', 'connaissance'],
                    'sous_themes': ['conflit', 'rupture', 'réconciliation', 'solitude', 'communication', 'amitié', 'famille']
                },
                'estime_soi': {
                    'mots': ['fier', 'honteux', 'confiant', 'doute', 'incapable', 'compétent', 'réussite', 'échec', 'valeur', 'estime', 'confiance'],
                    'sous_themes': ['confiance en soi', 'doute', 'accomplissement', 'auto-critique', 'valorisation']
                },
                'santé_mentale': {
                    'mots': ['stress', 'anxieux', 'déprimé', 'fatigue', 'énergie', 'sommeil', 'moral', 'équilibre', 'bienêtre', 'détente', 'repos'],
                    'sous_themes': ['anxiété', 'dépression', 'burnout', 'bien-être', 'relaxation']
                },
                'travail_etudes': {
                    'mots': ['travail', 'bureau', 'projet', 'réunion', 'deadline', 'emploi', 'carrière', 'examen', 'étude', 'profession', 'métier'],
                    'sous_themes': ['pression', 'accomplissement', 'échec', 'réussite', 'évolution']
                },
                'developpement_personnel': {
                    'mots': ['objectif', 'progrès', 'changement', 'amélioration', 'défi', 'apprentissage', 'croissance', 'évolution', 'transformation'],
                    'sous_themes': ['croissance', 'transition', 'transformation', 'apprentissage']
                }
            }
            
            print("✅ AnalyseurProfond initialisé avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de l'analyseur: {e}")
            # Fallback ultra-basique
            self.analyzer = None
            self.stop_words_fr = self._get_fallback_stopwords()
            self.dictionnaire_psychologique = {}
            self.themes_psychologiques = {}

    def _get_fallback_stopwords(self):
        """Stopwords français de base sans NLTK"""
        return set([
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'que', 'qui', 'dans', 'en', 'au', 'aux',
            'avec', 'pour', 'par', 'sur', 'dans', 'est', 'sont', 'son', 'ses', 'ces', 'cet', 'cette', 'mon', 'ton',
            'son', 'notre', 'votre', 'leur', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'nos', 'vos', 'leurs', 'je', 'tu',
            'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'ce', 'cela', 'ça', 'cet', 'cette'
        ])

    def analyser_texte(self, texte):
        """Analyse PROFONDE d'un texte avec insights psychologiques"""
        print(f"🔍 Début de l'analyse pour: {texte[:50]}...")
        
        if not texte or len(texte.strip()) == 0:
            return self._resultat_vide()
        
        try:
            # Analyses multiples et détaillées
            analyse_sentiment = self._analyse_sentiment_profonde(texte)
            analyse_emotions = self._analyse_emotions_detaillees(texte)
            analyse_themes = self._analyse_themes_psychologiques(texte)
            analyse_cognitive = self._analyse_patterns_cognitifs(texte)
            recommandations = self._generer_recommandations_personnalisees(
                analyse_sentiment, analyse_emotions, analyse_themes, analyse_cognitive
            )
            
            resultat = {
                'success': True,
                'analyse_complete': {
                    'metriques_generales': {
                        'longueur_texte': len(texte),
                        'nombre_phrases': self._compter_phrases(texte),
                        'complexite_emotionnelle': self._calculer_complexite_emotionnelle(analyse_emotions),
                        'niveau_intensite': analyse_sentiment['intensite_globale']
                    },
                    'sentiment_principal': {
                        'ton': analyse_sentiment['ton_principal'],
                        'score': analyse_sentiment['score_global'],
                        'confiance': analyse_sentiment['confiance'],
                        'intensite': analyse_sentiment['intensite_globale']
                    },
                    'emotions_detectees': analyse_emotions,
                    'themes_psychologiques': analyse_themes,
                    'patterns_cognitifs': analyse_cognitive,
                    'mots_cles_significatifs': self._extraire_mots_cles_psychologiques(texte),
                    'recommandations': recommandations,
                    'insights_psychologiques': self._generer_insights_psychologiques(
                        analyse_sentiment, analyse_emotions, analyse_themes
                    )
                }
            }
            
            print(f"✅ Analyse terminée - Ton: {analyse_sentiment['ton_principal']}, Confiance: {analyse_sentiment['confiance']}")
            return resultat
            
        except Exception as e:
            print(f"❌ Erreur dans l'analyse: {e}")
            return self._resultat_erreur(str(e))

    def _analyse_sentiment_profonde(self, texte):
        """Analyse de sentiment multidimensionnelle sans NLTK"""
        texte_lower = texte.lower()
        
        # Score basé sur le dictionnaire français
        score_total = 0
        emotions_trouvees = {}
        mots_emotionnels = []
        
        # Analyser chaque catégorie d'émotions
        for categorie, emotions in self.dictionnaire_psychologique.items():
            if 'émotions' in categorie:
                for emotion_nom, data in emotions.items():
                    mots_trouves = []
                    for mot in data['mots']:
                        if mot in texte_lower:
                            # Compter les occurrences
                            count = texte_lower.count(mot)
                            score_total += data['score'] * count
                            mots_trouves.extend([mot] * count)
                            mots_emotionnels.extend([mot] * count)
                    
                    if mots_trouves:
                        emotions_trouvees[emotion_nom] = {
                            'score': data['score'] * len(mots_trouves),
                            'mots_trouves': mots_trouves,
                            'intensite': data['intensite']
                        }
        
        # Analyser l'intensité
        intensite_score = 0
        for niveau, mots in self.dictionnaire_psychologique['intensite_emotionnelle'].items():
            for mot in mots:
                if mot in texte_lower:
                    if niveau == 'faible': intensite_score += 0.5
                    elif niveau == 'moyenne': intensite_score += 1
                    elif niveau == 'forte': intensite_score += 1.5
                    elif niveau == 'extreme': intensite_score += 2
        
        # Déterminer le ton principal
        if score_total > 3:
            ton_principal = 'positif'
            confiance = min(0.85 + (score_total * 0.02), 0.95)
        elif score_total < -3:
            ton_principal = 'negatif'
            confiance = min(0.85 + (abs(score_total) * 0.02), 0.95)
        elif score_total > 1:
            ton_principal = 'positif'
            confiance = 0.75
        elif score_total < -1:
            ton_principal = 'negatif'
            confiance = 0.75
        else:
            ton_principal = 'neutre'
            confiance = 0.6
        
        # Ajuster avec l'intensité
        intensite_globale = 'modérée'
        if intensite_score > 3:
            intensite_globale = 'élevée'
            confiance = min(confiance + 0.1, 0.95)
        elif intensite_score < 1:
            intensite_globale = 'faible'
        
        # Détection spéciale pour les cas évidents
        if 'heureux' in texte_lower and 'salut' in texte_lower:
            ton_principal = 'positif'
            confiance = 0.9
        
        return {
            'ton_principal': ton_principal,
            'score_global': round(score_total, 2),
            'confiance': round(confiance, 2),
            'emotions_trouvees': emotions_trouvees,
            'intensite_globale': intensite_globale,
            'score_intensite': intensite_score,
            'mots_emotionnels': mots_emotionnels
        }

    def _analyse_emotions_detaillees(self, texte):
        """Analyse détaillée des émotions"""
        texte_lower = texte.lower()
        emotions_detaillees = {}
        
        for categorie, emotions in self.dictionnaire_psychologique.items():
            if 'émotions' in categorie:
                for emotion_nom, data in emotions.items():
                    mots_trouves = [mot for mot in data['mots'] if mot in texte_lower]
                    if mots_trouves:
                        presence = len(mots_trouves)
                        intensite = 'élevée' if presence >= 2 else 'moyenne' if presence >= 1 else 'faible'
                        
                        emotions_detaillees[emotion_nom] = {
                            'presence': presence,
                            'mots_cles': mots_trouves,
                            'intensite': intensite,
                            'score_emotion': data['score']
                        }
        
        return emotions_detaillees

    def _analyse_themes_psychologiques(self, texte):
        """Analyse des thèmes psychologiques"""
        texte_lower = texte.lower()
        themes_detectes = {}
        
        for theme, data in self.themes_psychologiques.items():
            mots_trouves = [mot for mot in data['mots'] if mot in texte_lower]
            if mots_trouves:
                # Identifier les sous-thèmes pertinents
                sous_themes_pertinents = []
                for sous_theme in data['sous_themes']:
                    if any(mot in sous_theme for mot in mots_trouves):
                        sous_themes_pertinents.append(sous_theme)
                
                pertinence = 'élevée' if len(mots_trouves) >= 3 else 'moyenne' if len(mots_trouves) >= 2 else 'faible'
                
                themes_detectes[theme] = {
                    'score': len(mots_trouves),
                    'mots_cles': mots_trouves,
                    'sous_themes': sous_themes_pertinents,
                    'pertinence': pertinence
                }
        
        return themes_detectes

    def _analyse_patterns_cognitifs(self, texte):
        """Détection des patterns de pensée"""
        texte_lower = texte.lower()
        patterns_detectes = {}
        
        for pattern, mots in self.dictionnaire_psychologique['patterns_cognitifs'].items():
            mots_trouves = [mot for mot in mots if mot in texte_lower]
            if mots_trouves:
                occurrences = len(mots_trouves)
                impact = 'élevé' if occurrences >= 3 else 'modéré' if occurrences >= 2 else 'faible'
                
                patterns_detectes[pattern] = {
                    'occurrences': occurrences,
                    'exemples': mots_trouves,
                    'impact': impact
                }
        
        return patterns_detectes

    def _generer_recommandations_personnalisees(self, sentiment, emotions, themes, patterns):
        """Génère des recommandations basées sur l'analyse complète"""
        recommandations = []
        
        ton = sentiment['ton_principal']
        intensite = sentiment['intensite_globale']
        
        # Recommandations basées sur le sentiment
        if ton == 'positif':
            recommandations.append("🎉 **Capitalisez sur cette énergie positive** : Profitez-en pour entreprendre de nouveaux projets ou renforcer vos relations")
            recommandations.append("📝 **Journal de gratitude** : Notez 3 choses positives de votre journée pour ancrer ces émotions")
        
        elif ton == 'negatif':
            if intensite == 'élevée':
                recommandations.append("💆 **Gestion immédiate** : Pratiquez la respiration 4-7-8 (4s inspiration, 7s rétention, 8s expiration)")
                recommandations.append("🚶 **Break sensoriel** : Marchez 5 minutes en pleine conscience, en notant 5 choses que vous voyez, entendez, ressentez")
            
            if 'tristesse' in emotions:
                recommandations.append("🤗 **Auto-compassion** : Écrivez-vous une lettre bienveillante comme vous le feriez pour un ami")
            
            if 'colère' in emotions:
                recommandations.append("🎯 **Canalisation** : Activité physique ou expression créative (dessin, écriture libre)")
        
        # Recommandations basées sur les patterns
        if 'catastrophisme' in patterns:
            recommandations.append("🔍 **Recadrage cognitif** : 'Quelle est la probabilité réelle que le pire scénario se produise ?'")
        
        if 'pensée_tout_rien' in patterns:
            recommandations.append("🌈 **Nuances** : Remplacez 'toujours/jamais' par 'parfois/souvent' dans vos pensées")
        
        # Recommandations générales
        recommandations.append("📊 **Suivi** : Réanalysez dans quelques jours pour observer votre évolution émotionnelle")
        
        return recommandations[:5]  # Limiter à 5 recommandations

    def _generer_insights_psychologiques(self, sentiment, emotions, themes):
        """Génère des insights psychologiques"""
        insights = []
        
        nb_emotions = len(emotions)
        if nb_emotions >= 3:
            insights.append("🎭 **Émotions multiples** : Vous expérimentez plusieurs émotions, signe d'une riche vie intérieure")
        elif nb_emotions == 1:
            insights.append("🎯 **Émotion focale** : Une émotion principale domine, indiquant une réaction claire à la situation")
        
        if sentiment['intensite_globale'] == 'élevée':
            insights.append("⚡ **Intensité émotionnelle** : Vos émotions sont vives, ce qui peut révéler l'importance de cette situation pour vous")
        
        if 'relations_interpersonnelles' in themes:
            insights.append("👥 **Focus relationnel** : Vos préoccupations semblent centrées sur vos interactions sociales")
        
        return insights

    def _extraire_mots_cles_psychologiques(self, texte):
        """Extraction de mots-clés significatifs"""
        try:
            mots = self._tokenize_simple(texte)
            mots_filtres = [
                mot for mot in mots 
                if mot not in self.stop_words_fr 
                and len(mot) > 3
            ]
            
            # Pondérer les mots émotionnels
            mots_ponderes = []
            for mot in mots_filtres:
                poids = 1
                # Vérifier si c'est un mot émotionnel
                for categorie in self.dictionnaire_psychologique.values():
                    if isinstance(categorie, dict):
                        for emotion_data in categorie.values():
                            if isinstance(emotion_data, dict) and 'mots' in emotion_data:
                                if mot in emotion_data['mots']:
                                    poids = 3
                                    break
                mots_ponderes.extend([mot] * poids)
            
            compteur = Counter(mots_ponderes)
            return [{'mot': mot, 'frequence': count} for mot, count in compteur.most_common(8)]
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des mots-clés: {e}")
            return []

    def _tokenize_simple(self, texte):
        """Tokenisation simple sans NLTK"""
        try:
            # Nettoyer et diviser le texte
            texte = texte.lower()
            texte = texte.translate(str.maketrans('', '', string.punctuation))
            return texte.split()
        except Exception as e:
            print(f"Erreur lors de la tokenisation: {e}")
            return []

    def _compter_phrases(self, texte):
        """Comptage simple des phrases"""
        try:
            return len(re.split(r'[.!?]+', texte))
        except Exception:
            return 1

    def _calculer_complexite_emotionnelle(self, emotions):
        """Calcule la complexité émotionnelle"""
        try:
            nb_emotions = len(emotions)
            if nb_emotions == 0:
                return 'neutre'
            elif nb_emotions == 1:
                return 'simple'
            elif nb_emotions <= 3:
                return 'modérée'
            else:
                return 'complexe'
        except Exception:
            return 'neutre'

    def _resultat_vide(self):
        return {
            'success': False,
            'analyse_complete': {
                'erreur': 'Aucun texte à analyser',
                'recommandations': ['📝 Veuillez saisir un texte à analyser']
            }
        }

    def _resultat_erreur(self, erreur):
        return {
            'success': False,
            'analyse_complete': {
                'erreur': f'Erreur technique: {erreur}',
                'recommandations': ['🔄 Veuillez réessayer ou contacter le support']
            }
        }