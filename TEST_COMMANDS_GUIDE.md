# 🧪 Test Commands Guide - Complete Testing Workflow

## 📋 Main Test Command

### **`create_test_users`** ⭐ **RECOMMANDÉ** - Simple Test Setup

Creates test users with all necessary data for manual testing of all features.

```bash
python manage.py create_test_users
```

**What it creates:**
- **3 Users** with different profiles:
  - **Alice**: Développeuse, heureuse, intérêts tech (programmation, yoga, lecture)
  - **Bob**: Développeur, heureux, intérêts tech (code, fitness, lecture) → **High match with Alice (~38-45%)**
  - **Charlie**: Artiste, anxieux, intérêts créatifs (art, musique) → **Low match (below threshold)**
- **Journals**: 5 journal entries per user for AI analysis
- **Statistics**: Monthly statistics for PDF report generation

**Credentials (all passwords: `testpass123`):**
- Alice: `alice@test.com` / `testpass123`
- Bob: `bob@test.com` / `testpass123`
- Charlie: `charlie@test.com` / `testpass123`

**Features:**
- ✅ Idempotent (won't create duplicates if data exists)
- ✅ Safe to run multiple times
- ✅ Creates only essential data (users, journals, statistics)
- ✅ Lets you test features manually

---

## 🎯 Complete Testing Scenarios

### **Scenario 1: Connection Suggestions Testing** 🔗

#### **Setup:**
```bash
python manage.py create_test_users
```

#### **Test Steps:**

**1. Login as Alice:**
- Email: `alice@test.com`
- Password: `testpass123`

**2. Navigate to Suggestions:**
- Go to: `http://127.0.0.1:8000/communication/suggestions/`

**3. Generate Suggestions:**
- Click "Générer des suggestions" button
- ✅ Verify:
  - System calculates similarities
  - **Bob** suggestion appears with ~38-45% compatibility
  - Match type: "😊 Humeur proche" or "🎯 Objectifs similaires"
  - **Charlie** does NOT appear (low similarity below 35% threshold)

**4. Test Suggestion Display:**
- ✅ Verify suggestion card shows:
  - Compatibility score with progress bar
  - Match type icon and badge
  - Status: "Proposée"
  - Date of suggestion

**5. Test Profile View:**
- Click on Bob's suggestion card
- ✅ Verify sidebar shows:
  - Bob's profile information
  - Detailed compatibility breakdown:
    - Objectifs similarity (40% weight)
    - Intérêts similarity (35% weight)
    - Humeur similarity (15% weight)
    - Other factors (10% weight)
  - Recent journal entries
  - Similarity score badge

**6. Test Accepting a Suggestion:**
- Click "Accepter" on Bob's suggestion
- ✅ Verify:
  - Message: "Suggestion acceptée ! Une demande de connexion a été envoyée à Bob"
  - Status changes to "Acceptée"
  - Connection request sent to Bob

**7. Test Two-Way Connection Flow:**
- **Logout from Alice**
- **Login as Bob:** `bob@test.com` / `testpass123`
- Go to: `http://127.0.0.1:8000/communication/suggestions/`
- ✅ Verify:
  - Bob sees connection request from Alice
  - Can click "Accepter la demande"
  - After acceptance, connection is established

**8. Test Established Connections:**
- Click "Mes Connexions" tab (or go to `/communication/connexions/`)
- ✅ Verify:
  - Alice appears in Bob's connection list
  - Shows connection date
  - Can view full profile
  - Can remove connection if needed

**9. Test Filtering:**
- ✅ Filter by: "Toutes" / "Proposées" / "Acceptées" / "Ignorées"
- ✅ Verify counts update correctly

**10. Test Ignoring a Suggestion:**
- Find a suggestion with status "Proposée"
- Click "Ignorer"
- ✅ Verify:
  - Suggestion moves to "Ignorées" tab
  - Can still view but can't accept

---

### **Scenario 2: PDF Reports Testing** 📄

#### **Setup:**
```bash
python manage.py create_test_users
```

#### **Test Steps:**

**1. Login as Alice:**
- Email: `alice@test.com`
- Password: `testpass123`

**2. Navigate to PDF Reports:**
- Go to: `http://127.0.0.1:8000/communication/rapports/`

**3. Generate a New PDF Report:**
- Go to: `http://127.0.0.1:8000/communication/rapports/generer/`
- Select the statistics period (should see current month available)
- Customize report options:
  - **Format**: Complet / Résumé / Statistiques / Émotionnel / Hebdomadaire / Personnalisé
  - **Template**: Moderne / Classique / Minimaliste / Coloré / Sombre
  - **Color scheme**: Choose primary and secondary colors
  - **Sections to include**:
    - ✅ Statistiques
    - ✅ Graphiques
    - ✅ Analyse IA
    - ✅ Journaux
    - ✅ Objectifs
    - ✅ Recommandations
- Click "Générer le Rapport"
- ✅ Verify:
  - New PDF is generated
  - Appears in the reports list
  - Status shows "Terminé"

**4. Test PDF Viewing:**
- Click on the report to view details
- ✅ Verify report details page shows all information

**5. Test PDF Download:**
- Click "Télécharger" button
- ✅ Verify PDF downloads successfully
- ✅ Open PDF and verify it contains:
  - Statistics section
  - Graphs and charts (if included)
  - Journal entries (if included)
  - Objectives (if included)
  - Recommendations (if included)

**6. Test PDF Operations:**
- ✅ Duplicate a report
- ✅ Delete a report
- ✅ View report history

---

### **Scenario 3: AI Assistant Conversations** 🤖

#### **Setup:**
```bash
python manage.py create_test_users
```

#### **Test Steps:**

**1. Login as Alice:**
- Email: `alice@test.com`
- Password: `testpass123`

**2. Navigate to AI Assistant:**
- Go to: `http://127.0.0.1:8000/communication/assistant-ia/`
- You should see:
  - **Left sidebar**: List of 5 journals
  - **Center**: AI chat interface (larger section, scrollable)
  - **Right sidebar**: Statistics and conversation history (compact)

**3. Test Different Conversation Types:**

**a) Journal Analysis:**
- Click on a journal in the left sidebar (or attach it using paperclip button)
- Type: "Analyse mon journal"
- Press Enter or click Send
- ✅ Verify:
  - AI analyzes the journal content
  - Badge shows: "📊 Analyse Journal"
  - Response includes insights about the journal
  - Chat scrolls down automatically

**b) Writing Suggestions:**
- Type: "Donne-moi des idées d'écriture"
- ✅ Verify:
  - AI provides writing prompts
  - Badge shows: "✍️ Suggestion Écriture"

**c) Emotional Support:**
- Type: "Je me sens stressé, as-tu des conseils ?"
- ✅ Verify:
  - AI provides supportive response
  - Badge shows: "💖 Support Émotionnel"

**d) General Questions:**
- Type: "Comment créer un journal ?"
- ✅ Verify:
  - AI provides helpful guidance
  - Badge shows: "❓ Question"

**4. Test Chat Features:**
- ✅ Send multiple messages in same session
- ✅ Verify chat scrolls automatically to bottom
- ✅ Verify message history persists when reloading
- ✅ Test quick prompt buttons (in welcome screen)
- ✅ Verify journal attachment works (paperclip button)
- ✅ Verify keyboard shortcut (Enter to send)

**5. Test Conversation History:**
- Go to: `http://127.0.0.1:8000/communication/assistant-ia/historique/`
- ✅ Verify:
  - List of previous sessions (compact sidebar on left)
  - Click a session to view conversation
  - Messages display correctly with badges
  - Type badges are visible and colored correctly
  - Export conversation works

---

### **Scenario 4: Complete User Journey** 🎬

#### **Setup:**
```bash
python manage.py create_test_users
```

#### **Complete Workflow:**

**Day 1 - Alice's Journey:**

1. **Morning - Login & Check Dashboard**
   - Login: `alice@test.com` / `testpass123`
   - ✅ Verify dashboard shows statistics overview

2. **Morning - View Journals**
   - Go to Journal section
   - ✅ Verify 5 journal entries are visible
   - ✅ Can view journal details

3. **Afternoon - Use AI Assistant**
   - Go to: `/communication/assistant-ia/`
   - Click on a journal entry in left sidebar
   - Ask: "Qu'est-ce que tu penses de mon journal ?"
   - ✅ Verify AI analyzes and provides insights

4. **Afternoon - Generate & Check Suggestions**
   - Go to: `/communication/suggestions/`
   - Click "Générer des suggestions"
   - ✅ Verify Bob is suggested (high compatibility)
   - View Bob's profile with similarity breakdown
   - Accept the suggestion

5. **Evening - Generate PDF Report**
   - Go to: `/communication/rapports/generer/`
   - Select current month statistics
   - Customize options (choose "Complet" format, "Moderne" template)
   - Generate report
   - ✅ Verify PDF is created and downloadable

**Day 2 - Bob's Journey:**

1. **Morning - Check Connection Request**
   - Login: `bob@test.com` / `testpass123`
   - Go to: `/communication/suggestions/`
   - ✅ Verify Alice's connection request
   - Accept it to establish connection

2. **Afternoon - View Established Connections**
   - Go to: `/communication/connexions/`
   - ✅ Verify Alice is in connections list
   - Click to view her profile
   - ✅ Verify compatibility details shown

3. **Evening - AI Conversation**
   - Go to: `/communication/assistant-ia/`
   - Have a conversation about productivity or fitness
   - ✅ Verify conversation is saved
   - Check history: `/communication/assistant-ia/historique/`

**Day 3 - Charlie's Journey:**

1. **Morning - Check Suggestions**
   - Login: `charlie@test.com` / `testpass123`
   - Go to: `/communication/suggestions/`
   - Generate suggestions
   - ✅ Verify NO suggestions appear (Charlie's profile too different)
   - This demonstrates the similarity threshold working correctly

2. **Afternoon - Use AI for Support**
   - Go to: `/communication/assistant-ia/`
   - Ask for emotional support: "Je me sens anxieux, as-tu des conseils ?"
   - ✅ Verify AI provides supportive response

---

## 📊 Expected Test Results

### **Similarity Scores:**

**Alice ↔ Bob:**
- **Expected Score**: ~38-45%
- **Match Type**: `humeur_proche` (both "heureux") or `objectif_similaire`
- **Why:**
  - ✅ 100% mood match (both "heureux")
  - ✅ 40-50% interests match (Programmation, Lecture)
  - ✅ 20-30% objectives match (both learning-related)
  - ✅ Above 35% threshold → **Will generate suggestion**

**Alice ↔ Charlie:**
- **Expected Score**: ~5-10% (BELOW THRESHOLD)
- **Why:**
  - ❌ Different objectives (tech vs art)
  - ❌ Different interests
  - ❌ Different moods (heureux vs anxieux)
  - ❌ Below 35% threshold → **Will NOT generate suggestion**

**Bob ↔ Charlie:**
- **Expected Score**: ~5-10% (BELOW THRESHOLD)
- **Why:** Similar to Alice ↔ Charlie

---

## 🔧 Troubleshooting

### **No suggestions appear after generating?**
1. **Check user profiles have data:**
   - Login as Alice
   - Verify profile has: `objectifs_personnels`, `centres_interet`, `humeur_generale`
   - If empty, run `create_test_users` again

2. **Check similarity threshold:**
   - Minimum: 35% (see `SuggestionConnexionService.MIN_SIMILARITY_SCORE`)
   - Alice ↔ Bob should pass (~38-45%)
   - Alice ↔ Charlie will NOT pass (~5-10%)

3. **Check console logs:**
   - Look for any errors during suggestion generation
   - Verify MongoDB/Djongo connection is working

### **PDF not generating?**
1. **Check statistics exist:**
   - Run `create_test_users` to ensure statistics are created
   - Verify statistics appear in `/communication/rapports/generer/` dropdown

2. **Check PDF service:**
   - Verify WeasyPrint or report generation library is installed
   - Check console for error messages
   - Verify file permissions in `media/rapports_pdf/` directory

3. **Check report status:**
   - If status is "en_cours", wait a moment and refresh
   - If status is "erreur", check console logs for details

### **AI conversations not saving?**
1. **Check AI service configuration:**
   - Verify `OPENROUTER_API_KEY` is set in environment
   - Check console for API errors
   - Test with simple message first

2. **Check journal attachment:**
   - If attaching journal fails, verify journal model exists
   - Try without journal attachment first

3. **Check conversation history:**
   - Verify `AssistantIA` model is saving correctly
   - Check database for conversation records

### **Djongo/MongoDB errors?**
- The suggestion service filters in Python to avoid Djongo compatibility issues
- If errors persist:
  - Check MongoDB connection
  - Verify database is running
  - Check if error is related to user query (should be handled by fallback)

---

## 📝 Quick Command Reference

| Command | Purpose | Creates Users | Creates Journals | Creates Stats | PDF Reports | IA Conversations | Suggestions |
|---------|---------|---------------|------------------|---------------|-------------|------------------|-------------|
| `create_test_users` | ⭐ Simple test setup | ✅ (Alice, Bob, Charlie) | ✅ (5 each) | ✅ | ❌ (manual) | ❌ (manual) | ❌ (manual) |

**Note:** `create_test_users` creates only the essential data. You test PDF generation and AI conversations manually through the UI.

---

## 🚀 Quick Start Guide

### **1. Clean & Setup (Fresh Start):**
```bash
# Optional: Clean previous test data
python manage.py clean_test_suggestions --all-test

# Create test users with journals and statistics
python manage.py create_test_users
```

### **2. Test Features (In Order):**

**a) Test Suggestions:**
```bash
# 1. Login as Alice: alice@test.com / testpass123
# 2. Go to: http://127.0.0.1:8000/communication/suggestions/
# 3. Click "Générer des suggestions"
# 4. Verify Bob appears with ~38-45% compatibility
# 5. Accept suggestion, then login as Bob to accept connection
```

**b) Test PDF Reports:**
```bash
# 1. Login as Alice: alice@test.com / testpass123
# 2. Go to: http://127.0.0.1:8000/communication/rapports/generer/
# 3. Select statistics period
# 4. Customize report options
# 5. Click "Générer le Rapport"
# 6. Download and verify PDF content
```

**c) Test AI Assistant:**
```bash
# 1. Login as Alice: alice@test.com / testpass123
# 2. Go to: http://127.0.0.1:8000/communication/assistant-ia/
# 3. Click on a journal entry (left sidebar)
# 4. Ask: "Analyse mon journal"
# 5. Verify AI response with badge
# 6. Check history: /communication/assistant-ia/historique/
```

---

## 🎯 Testing Checklist

Use this checklist to verify all features work:

### **Suggestions:**
- [ ] Generate suggestions button works
- [ ] Bob appears with high compatibility (~38-45%)
- [ ] Charlie does NOT appear (below threshold)
- [ ] Profile sidebar shows detailed compatibility breakdown
- [ ] Accept suggestion sends connection request
- [ ] Two-way connection flow works (Bob accepts)
- [ ] Established connections page shows connected users
- [ ] Filter tabs work (Toutes, Proposées, Acceptées, Ignorées)

### **PDF Reports:**
- [ ] Report generation page loads
- [ ] Statistics dropdown shows available periods
- [ ] Can customize format, template, colors
- [ ] Can select which sections to include
- [ ] PDF generates successfully
- [ ] Report appears in list with "Terminé" status
- [ ] Can download PDF
- [ ] PDF contains expected content (stats, journals, etc.)
- [ ] Can duplicate and delete reports

### **AI Assistant:**
- [ ] Assistant page loads with journals sidebar
- [ ] Can select journal entries
- [ ] Can send messages
- [ ] Journal analysis works with badge
- [ ] Writing suggestions work with badge
- [ ] Emotional support works with badge
- [ ] General questions work with badge
- [ ] Chat auto-scrolls to bottom
- [ ] Conversation history saves correctly
- [ ] History page shows all sessions
- [ ] Can export conversations

---

**Happy Testing! 🚀**

For issues, check console logs and verify:
1. All models are properly installed
2. Database connection is working
3. Required services are configured (OpenRouter API key for AI, PDF library for reports)
