# setup_nltk.py
import nltk
import os

def download_nltk_resources():
    print("📥 Téléchargement des ressources NLTK...")
    
    resources = [
        'punkt',           # Tokenizer
        'stopwords',       # Mots vides
        'vader_lexicon',   # Analyseur de sentiment
        'averaged_perceptron_tagger',  # POS tagging
        'wordnet'          # Dictionnaire sémantique
    ]
    
    for resource in resources:
        try:
            print(f"Vérification de {resource}...")
            nltk.data.find(resource)
            print(f"✅ {resource} déjà installé")
        except LookupError:
            print(f"📥 Téléchargement de {resource}...")
            nltk.download(resource)
            print(f"✅ {resource} téléchargé avec succès")
    
    print("🎉 Toutes les ressources NLTK sont prêtes!")

if __name__ == "__main__":
    download_nltk_resources()