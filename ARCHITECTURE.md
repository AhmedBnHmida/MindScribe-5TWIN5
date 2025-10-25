# MindScribe - Architecture Documentation

## 📐 Application Structure

MindScribe is organized into **6 Django apps** following a modular architecture based on the class diagram.

---

## 🏗️ Apps Overview

### 1. **users** - User Management
**Purpose**: Authentication, user profiles, and session management

**Models**:
- **CustomUser**: Extended Django user model with comprehensive user attributes
  - Basic info: email, phone, photo, role (user/admin)
  - Personal info: age, sexe, état civil, adresse, langue
  - Professional: status_professionnel, profession
  - Personality: casanier, sociable, centres_interet, passions
  - Mental health: humeur_generale, niveau_stress, qualite_sommeil
  - Physical health: niveau_activite_physique, habitudes_alimentaires, heures_sommeil_par_nuit
  - Writing preferences: frequence_ecriture_souhaitee, moment_prefere_ecriture
  - Goals: objectifs_personnels
  - Routine: routine_quotidienne, preferences_suivi
  
- **Session**: User session tracking
  - utilisateur (FK → CustomUser)
  - date_connexion, adresse_ip, actif

**Admin**: Fully configured admin with organized fieldsets

**URLs**: `/`, `/home/`, `/login/`, `/logout/`, `/register/`, `/profile/edit/`

---

### 2. **journal** - Multimodal Journal
**Purpose**: Capture and store user journal entries (text, audio, image)

**Models**:
- **Journal**: Multimodal journal entries
  - utilisateur (FK → CustomUser)
  - date_creation
  - categorie
  - contenu_texte (TextField)
  - audio (FileField)
  - image (ImageField)
  - type_entree: ['texte', 'audio', 'image']

**Relationships**:
- User → Journal (One-to-Many)

**Admin**: Configured with filtering by type and date

**URLs**: `/journal/` (placeholder - to be implemented)

---

### 3. **analysis** - AI Analysis
**Purpose**: AI-powered analysis of journal entries

**Models**:
- **AnalyseIA**: AI analysis results
  - journal (OneToOne → Journal)
  - mots_cles (JSONField)
  - ton_general: ['positif', 'neutre', 'negatif']
  - themes_detectes (JSONField)
  - resume_journee (TextField)
  - date_analyse

**Relationships**:
- Journal → AnalyseIA (One-to-One)
- AnalyseIA → Statistique (Many-to-Many)

**Admin**: Configured with search by themes and mood

**URLs**: `/analysis/` (placeholder - to be implemented)

---

### 4. **dashboard** - Statistics & Visualization
**Purpose**: Track and visualize user statistics and trends

**Models**:
- **Statistique**: Aggregated user statistics
  - utilisateur (FK → CustomUser)
  - periode (e.g., "Janvier 2024")
  - frequence_ecriture (int)
  - score_humeur (float)
  - themes_dominants (JSONField)
  - bilan_mensuel (TextField)
  - analyses_liees (M2M → AnalyseIA)
  - date_creation, date_mise_a_jour

**Relationships**:
- User → Statistique (One-to-Many)
- Statistique ↔ AnalyseIA (Many-to-Many)
- Statistique → RapportPDF (One-to-One)

**Admin**: Configured with filtering and M2M selection

**URLs**: `/dashboard/` (placeholder - to be implemented)

---

### 5. **recommendations** - Recommendations & Goals
**Purpose**: Provide personalized recommendations and track user goals

**Models**:
- **Recommandation**: Personalized recommendations
  - utilisateur (FK → CustomUser)
  - statistique (FK → Statistique, nullable)
  - type: ['bien_etre', 'productivite', 'sommeil', 'nutrition']
  - contenu (TextField)
  - date_emission
  - statut: ['nouvelle', 'suivie', 'ignoree']

- **Objectif**: User personal goals
  - utilisateur (FK → CustomUser)
  - nom, description
  - progres (float, %)
  - date_debut, date_fin
  - date_creation, date_mise_a_jour
  - Property: `est_termine` (progres >= 100)

**Relationships**:
- User → Recommandation (One-to-Many)
- Statistique → Recommandation (One-to-Many, optional)
- User → Objectif (One-to-Many)

**Admin**: Configured with custom display for completion status

**URLs**: `/recommendations/` (placeholder - to be implemented)

---

### 6. **communication** - Communication & Reports
**Purpose**: PDF reports, AI assistant, and user connection suggestions

**Models**:
- **RapportPDF**: Monthly PDF reports
  - statistique (OneToOne → Statistique)
  - mois (e.g., "Janvier 2024")
  - contenu_pdf (FileField)
  - date_generation

- **AssistantIA**: AI assistant conversations
  - utilisateur (FK → CustomUser)
  - journal (FK → Journal, nullable)
  - message_utilisateur (TextField)
  - reponse_ia (TextField)
  - date_interaction

- **SuggestionConnexion**: User connection suggestions
  - utilisateur_source (FK → CustomUser)
  - utilisateur_cible (FK → CustomUser)
  - score_similarite (float)
  - type_suggestion: ['objectif_similaire', 'humeur_proche', 'interet_commun']
  - date_suggestion
  - statut: ['proposee', 'acceptee', 'ignoree']
  - Unique constraint: (utilisateur_source, utilisateur_cible)

**Relationships**:
- Statistique → RapportPDF (One-to-One)
- User → AssistantIA (One-to-Many)
- Journal → AssistantIA (One-to-Many, optional)
- User → SuggestionConnexion (One-to-Many, bidirectional)

**Admin**: Configured for all models with proper filtering

**URLs**: `/communication/` (placeholder - to be implemented)

---

## 🔗 Complete Relationship Map

```
CustomUser
  ├─→ Session (1:N)
  ├─→ Journal (1:N)
  │    └─→ AnalyseIA (1:1)
  │         └─→ Statistique (N:M)
  ├─→ Statistique (1:N)
  │    ├─→ RapportPDF (1:1)
  │    └─→ Recommandation (1:N)
  ├─→ Recommandation (1:N)
  ├─→ Objectif (1:N)
  ├─→ AssistantIA (1:N)
  ├─→ SuggestionConnexion (1:N source)
  └─→ SuggestionConnexion (1:N cible)

Journal
  └─→ AssistantIA (1:N, optional)
```

---

## 📊 Database Schema Summary

### Primary IDs
All models use **UUID** as primary key (except CustomUser which uses Django's default ID + uuid field)

### File Uploads
- **User photos**: `media/user_photos/`
- **Journal audio**: `media/journal_audio/`
- **Journal images**: `media/journal_images/`
- **PDF reports**: `media/rapports_pdf/`

### JSON Fields
Used for flexible data storage:
- `centres_interet`, `passions`, `objectifs_personnels` (User)
- `adresse`, `routine_quotidienne`, `preferences_suivi` (User)
- `mots_cles`, `themes_detectes` (AnalyseIA)
- `themes_dominants` (Statistique)

---

## 🎯 Features by App

### ✅ Implemented (users app)
- User registration & login
- Profile management
- Session tracking
- Extended user attributes

### 🚧 To Implement

#### journal app
- [ ] Create journal entries (text/audio/image)
- [ ] List and filter entries
- [ ] Edit/Delete entries
- [ ] Category management

#### analysis app
- [ ] Automatic AI analysis on entry creation
- [ ] Sentiment analysis integration
- [ ] Theme detection
- [ ] Daily summaries

#### dashboard app
- [ ] Statistics calculation
- [ ] Mood tracking graphs
- [ ] Activity visualizations
- [ ] Monthly reports

#### recommendations app
- [ ] Recommendation engine
- [ ] Goal tracking interface
- [ ] Progress visualization
- [ ] Notification system

#### communication app
- [ ] PDF report generation
- [ ] AI chatbot interface
- [ ] User similarity algorithm
- [ ] Connection suggestions

---

## 🛠️ Technology Stack

- **Framework**: Django 3.2.21
- **Database**: MongoDB Atlas (via Djongo 1.3.6)
- **Frontend**: Bootstrap 5.1.3, Font Awesome 6.0
- **Storage**: Django FileField/ImageField (media uploads)
- **Authentication**: Django Auth + Custom User Model

---

## 📝 Next Steps

1. **Implement Views**: Create views for each app's functionality
2. **Create Templates**: Build UI for journal entries, dashboard, etc.
3. **AI Integration**: Connect AI services for analysis
4. **API Development**: Consider Django REST Framework for mobile app
5. **Testing**: Write unit tests for all models and views
6. **Deployment**: Configure for production with proper media serving

---

## 🔐 Security Considerations

- All models have proper foreign key relationships with CASCADE/SET_NULL
- User sessions are tracked with IP addresses
- File uploads are organized by type
- UUIDs provide non-sequential IDs for security
- Role-based access control (user/admin)

---

## 📚 Documentation

For detailed implementation, see:
- `users/models.py` - Extended user model
- `journal/models.py` - Journal entry model
- `analysis/models.py` - AI analysis model
- `dashboard/models.py` - Statistics model
- `recommendations/models.py` - Recommendations & goals
- `communication/models.py` - Reports & connections

All models are registered in Django admin for easy management.

