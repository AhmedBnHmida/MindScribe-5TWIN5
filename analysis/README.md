# Module d'Analyse Intelligente & Résumé IA

Ce module implémente l'analyse multimodale des entrées de journal, capable de traiter du texte, des images et de l'audio pour en extraire des informations pertinentes.

## Fonctionnalités

- **Analyse de sentiment**: Détection du ton général (positif, neutre, négatif)
- **Extraction de mots-clés**: Identification des termes importants dans le texte
- **Détection de thèmes**: Catégorisation du contenu par thèmes
- **Résumé automatique**: Génération d'un résumé concis en français
- **Transcription audio**: Conversion de fichiers audio en texte
- **Description d'images**: Génération de légendes pour les images
- **Classification de scènes**: Identification du type de scène dans une image

## Architecture

Le module est construit autour des composants suivants:

- **API REST**: Endpoint `/api/analyse/` pour traiter les requêtes multimodales
- **Modèles AI**: Utilisation de modèles Hugging Face pour les différentes tâches d'analyse
- **Stockage**: Intégration avec les modèles Journal pour sauvegarder les résultats

## Modèles AI utilisés

| Tâche | Modèle | Description |
|------|--------|-------------|
| Sentiment | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | Analyse de sentiment multilingue |
| Mots-clés | `KeyBERT` + `paraphrase-multilingual-MiniLM-L12-v2` | Extraction de mots-clés avec embeddings multilingues |
| Résumé | `facebook/mbart-large-50-many-to-many-mmt` | Génération de résumés en français |
| Transcription | `openai/whisper-small` | Reconnaissance vocale multilingue |
| Description d'images | `nlpconnect/vit-gpt2-image-captioning` | Génération de légendes pour images |
| Classification d'images | `google/vit-base-patch16-224` | Identification de scènes dans les images |

## Utilisation de l'API

### Endpoint

```
POST /api/analyse/
```

### Paramètres d'entrée

L'API accepte les paramètres suivants:

- `text` (optionnel): Texte à analyser
- `audio_file` (optionnel): Fichier audio à transcrire (formats: mp3, wav)
- `image_file` (optionnel): Image à analyser (formats: jpg, png)
- `user_id` (optionnel): ID de l'utilisateur pour sauvegarder l'analyse

Au moins un des paramètres `text`, `audio_file` ou `image_file` doit être fourni.

### Exemple de requête

```python
import requests

# Exemple avec texte uniquement
response = requests.post(
    'http://localhost:8000/api/analyse/',
    data={'text': "Aujourd'hui, j'ai eu une réunion productive avec mon équipe."}
)

# Exemple avec texte et image
files = {'image_file': open('photo.jpg', 'rb')}
data = {'text': "J'ai passé une belle journée au parc."}
response = requests.post(
    'http://localhost:8000/api/analyse/',
    data=data,
    files=files
)
```

### Format de réponse

```json
{
  "sentiment": "positif",
  "emotion_score": 0.85,
  "keywords": ["travail", "réunion", "productif"],
  "summary": "Aujourd'hui, tu as eu une réunion productive avec ton équipe.",
  "topics": ["travail", "réunion"],
  "audio_transcription": "",
  "image_caption": "un groupe de personnes dans un parc",
  "image_scene": "park"
}
```

## Tests

Un script de test `test_api.py` est disponible pour tester l'API avec différents types de contenu:

```bash
python analysis/test_api.py
```

## Dépendances

Les dépendances nécessaires sont listées dans `requirements.txt`. Assurez-vous d'installer ces dépendances avant d'utiliser le module:

```bash
pip install -r requirements.txt
```

## Limitations connues

- Les modèles AI sont chargés au démarrage du serveur, ce qui peut prendre du temps
- L'analyse d'images et la transcription audio peuvent être lentes sans GPU
- Les modèles sont optimisés pour le français mais peuvent fonctionner avec d'autres langues avec des performances variables

