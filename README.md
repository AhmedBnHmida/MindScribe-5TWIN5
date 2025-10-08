# MindScribe - Journal Personnel Intelligent

Journal IA multimodal avec analyse émotionnelle et recommandations personnalisées.

## 🚀 Fonctionnalités

- 📝 **Saisie multimodale** : Texte, audio et images
- 🎯 **Analyse émotionnelle** par IA
- 📊 **Tableau de bord** des humeurs et tendances
- 💡 **Recommandations personnalisées** pour le bien-être
- 📍 **Géolocalisation** des entrées
- 🔍 **Recherche intelligente** dans le journal

---

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Git
- Pip

### Configuration

1. **Cloner le projet**
```bash
git clone https://github.com/AhmedBnHmida/MindScribe-5TWIN5.git
cd MindScribe-5TWIN5
```

2. **Créer l'environnement virtuel**
```bash
virtualenv env_mindscribe
```

3. **Activer l'environnement**
```bash
# Windows
env_mindscribe\Scripts\activate

# Linux/Mac
source env_mindscribe/bin/activate
```

4. **Installer les dépendances**
```bash
pip install Django==4.2
```

5. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

6. **Accéder à l'application**
Ouvrez http://127.0.0.1:8000 dans votre navigateur

---

## 📁 Structure du projet
```bash
MindScribe/
├── manage.py
├── mindscribe/          # Configuration du projet
├── env_mindscribe/      # Environnement virtuel
├── .gitignore
└── README.md
```

---

## 👥 Développement
### Créer une nouvelle application
```bash
python manage.py startapp nom_application
```
### Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
### Créer un superutilisateur
```bash
python manage.py createsuperuser
```