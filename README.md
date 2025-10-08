# MindScribe - Journal Personnel Intelligent

Journal IA multimodal avec analyse émotionnelle et recommandations personnalisées.

## 🎯 Fonctionnalités

### 🔐 Authentification & Sécurité
- **Inscription/Connexion** avec email ou nom d'utilisateur
- **Rôles utilisateurs** (Utilisateur, Administrateur)
- **Sessions sécurisées** avec Django Auth
- **Redirection intelligente** selon le rôle

### 📝 Gestion du Journal
- **Saisie multimodale** : Texte, audio et images
- **Entrées datées** avec horodatage automatique
- **Géolocalisation** des entrées
- **Recherche intelligente** dans le journal

### 🧠 Analyse IA
- **Analyse émotionnelle** automatique des entrées
- **Recommandations personnalisées** pour le bien-être
- **Résumés quotidiens** générés par IA
- **Tendances émotionnelles** sur le long terme

### 📊 Visualisation
- **Tableau de bord** des humeurs et tendances
- **Graphiques d'évolution** émotionnelle
- **Statistiques personnalisées**
- **Historique complet** des entrées

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- PostgreSQL 12+
- Git

### Installation

1. **Cloner le projet**
```bash
git clone https://github.com/AhmedBnHmida/MindScribe-5TWIN5.git
cd MindScribe-5TWIN5
```

2. **Configuration l'environnement virtuel**
```bash
# Créer l'environnement virtuel
virtualenv env_mindscribe

# Activer l'environnement
# Windows
env_mindscribe\Scripts\activate
# Linux/Mac
source env_mindscribe/bin/activate
```

3. **Installer les dépendances**
```bash
pip install Django==4.2
```

4. **Configuration de la base de données**
```bash
# Créer la base PostgreSQL
createdb mindscribe_db

# Appliquer les migrations
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```


6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

7. **Accéder à l'application**
Ouvrez http://127.0.0.1:8000 dans votre navigateur

---

## 🗃️ Configuration Base de Données

### PostgreSQL
Le projet utilise PostgreSQL comme base de données principale. Configuration dans mindscribe/settings.py :

```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mindscribe_db',
        'USER': 'postgres',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Modèles Utilisateurs

- **CustomUser** : Modèle utilisateur personnalisé avec rôles

- **Champs étendus** : email, téléphone, rôle, bio

---

## 📁 Structure du projet
```bash
MindScribe/
├── 📁 mindscribe/           # Configuration du projet Django
├── 📁 users/                # Application d'authentification
│   ├── models.py           # Modèle CustomUser
│   ├── views.py            # Vues d'authentification
│   ├── urls.py             # Routes utilisateurs
│   └── admin.py            # Interface admin personnalisée
├── 📁 templates/           # Templates organisés
│   ├── auth/               # Templates d'authentification
│   ├── commun/             # Templates communs
│   └── views/              # Templates des vues spécifiques
├── 📁 static/              # Fichiers statiques (CSS, JS, images)
├── 📁 media/               # Fichiers uploadés par les utilisateurs
├── manage.py
├── requirements.txt
└── README.md
```

---

## 👥 Développement

### Structure des Applications

```bash
# Créer une nouvelle application
python manage.py startapp nom_application

# Générer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

### Commandes Utiles

```bash
# Lancer les tests
python manage.py test

# Vérifier le code
python manage.py check

# Collecter les fichiers statiques
python manage.py collectstatic
```

### Workflow Git
```bash
# Créer une nouvelle feature
git checkout -b feature/nouvelle-fonctionnalite

# Pousser une branche
git push -u origin feature/nouvelle-fonctionnalite

# Créer une Pull Request sur GitHub
```

---

## 🔧 Configuration
### Variables d'Environnement
Créez un fichier .env à la racine :

```bash
DEBUG=True
SECRET_KEY=votre_secret_key
DB_NAME=mindscribe_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```
### Applications Installées

- **users** - Authentification et gestion des utilisateurs

- **journal** - Application principale du journal (à venir)

- **django.contrib.admin** - Interface d'administration

- **django.contrib.auth** - Système d'authentification

---

## 🤝 Contribution

1. Fork le projet

2. Créer une branche feature (git checkout -b feature/AmazingFeature)

3. Commit les changements (git commit -m 'Add some AmazingFeature')

4. Push la branche (git push origin feature/AmazingFeature)

5. Ouvrir une Pull Request

