# 🧪 Test Commands Guide - Suggestion Connection System

## 📋 Available Test Commands

### 1. **`test_suggestion_logic`** - Test Similarity Algorithm
Tests the enhanced similarity calculation without database complexity.

```bash
python manage.py test_suggestion_logic
```

**What it does:**
- Creates 3 test users (Alice, Bob, Charlie) with different profiles
- Calculates similarity scores between them
- Shows detailed breakdowns (objectifs, intérêts, humeur, other)
- Creates a sample suggestion with real calculated score
- Does NOT require database access (avoids Djongo issues)

**Output:**
```
Alice <-> Bob:
  Overall Score: 38.75%
  Type: humeur_proche
  Detailed Scores:
    objectif_similaire: 20.00%
    interet_commun: 40.00%
    humeur_proche: 100.00%
    other: 17.50%
```

---

### 2. **`create_two_users_test`** - Create Test Users for UI Testing
Creates Alice and Bob with profiles that match well, using real similarity calculations.

```bash
python manage.py create_two_users_test
```

**What it does:**
- Creates Alice and Bob with matching profiles:
  - **Alice**: Développeuse, objectifs=["Apprendre Django", "Méditation"], intérêts=["Programmation", "Yoga", "Lecture"]
  - **Bob**: Développeur, objectifs=["Apprendre Python", "Fitness"], intérêts=["Programmation", "Fitness", "Lecture"]
  - Both have `humeur_generale='heureux'` (same mood = high match)
- Calculates real similarity score using `SuggestionConnexionService`
- Creates suggestion with calculated score and type
- Creates test journals for both users
- Password: `testpass123` for both

**Usage:**
1. Run this command
2. Login with `alice@test.com` / `testpass123`
3. Go to `/communication/suggestions/`
4. See the suggestion with **real compatibility score** and detailed breakdown
5. Click suggestion to see profile with similarity analysis

---

### 3. **`clean_test_suggestions`** - Clean Up Test Data
Removes test users and suggestions for fresh testing.

```bash
# Clean Alice and Bob only (default)
python manage.py clean_test_suggestions

# Clean only suggestions (keep users)
python manage.py clean_test_suggestions --suggestions-only

# Clean only users (keep suggestions)
python manage.py clean_test_suggestions --users-only

# Clean ALL test users (alice, bob, charlie, test_user_*, testuser_pdf)
python manage.py clean_test_suggestions --all-test
```

**What it cleans:**
- Test users: `alice@test.com`, `bob@test.com`, `charlie@test.com`, `test_pdf@mindscribe.com`
- Test usernames: `alice_test`, `bob_test`, `test_user_alice`, `test_user_bob`, `test_user_charlie`, `testuser_pdf`
- All suggestions involving these users

---

### 4. **`create_test_data`** - Complete Test Data Setup
Creates comprehensive test data including suggestions if other users exist.

```bash
python manage.py create_test_data
```

**What it does:**
- Creates user: `test_pdf@mindscribe.com` / `testpass123`
- Creates statistics, journals, analyses, recommendations, PDF reports
- **Automatically creates suggestions** if other users exist in database
- Uses real similarity calculations

**Integration:**
```bash
# Full workflow:
python manage.py clean_test_suggestions --all-test  # Clean everything
python manage.py create_two_users_test              # Create Alice & Bob
python manage.py create_test_data                   # Create test data + suggestions
```

---

## 🔄 Complete Testing Workflow

### **Option 1: Quick Test (2 users)**
```bash
# 1. Clean up
python manage.py clean_test_suggestions

# 2. Create test users with suggestions
python manage.py create_two_users_test

# 3. Test in browser
# Login: alice@test.com / testpass123
# Visit: http://127.0.0.1:8000/communication/suggestions/
```

### **Option 2: Full Test (multiple users + data)**
```bash
# 1. Clean everything
python manage.py clean_test_suggestions --all-test

# 2. Create Alice and Bob
python manage.py create_two_users_test

# 3. Create additional test data (will also create suggestions)
python manage.py create_test_data

# 4. Test similarity algorithm
python manage.py test_suggestion_logic

# 5. Test in browser with multiple users
```

---

## 🎯 What You'll See in the UI

### **Suggestion List View** (`/communication/suggestions/`)

1. **Suggestion Cards** show:
   - ✅ **Compatibility Score** (progress bar): e.g., 38.75%
   - ✅ **Match Type Icon**: 🎯 Objectifs similaires / 😊 Humeur proche / ⭐ Intérêts communs
   - ✅ **Status Badge**: Proposée / Acceptée / Ignorée
   - ✅ **Date** of suggestion

2. **Profile Sidebar** (when clicking a suggestion):
   - ✅ **Compatibility Analysis Card**:
     - Overall score with visual progress bar
     - Primary match reason
     - Detailed score breakdown:
       - 🎯 Objectifs (40% weight): X%
       - ⭐ Intérêts (35% weight): X%
       - 😊 Humeur (15% weight): X%
       - 💼 Autres (10% weight): X%
   - ✅ User profile: objectifs, intérêts, passions, humeur
   - ✅ Recent journal entries

### **User Profile View** (`/communication/profil/<user_id>/`)

- ✅ Similarity score badge in header
- ✅ Detailed compatibility breakdown section
- ✅ Shows which fields affect the score (with weights)
- ✅ Connection status (Connecté / Non connecté)

---

## 📊 Expected Similarity Scores

### **Alice ↔ Bob** (from `create_two_users_test`)
- **Expected Score**: ~38-40%
- **Match Type**: `humeur_proche` (both heureux)
- **Why:**
  - ✅ 100% mood match (both "heureux")
  - ✅ 40% interests match (Programmation, Lecture)
  - ✅ 20% objectives match (both learning-related)

### **Alice ↔ Charlie** (from `test_suggestion_logic`)
- **Expected Score**: ~4-5% (BELOW THRESHOLD)
- **Why:**
  - Different objectives
  - Different interests
  - Different moods (heureux vs anxieux)
  - ❌ Would NOT generate suggestion

---

## 🔧 Troubleshooting

### **No suggestions appear?**
1. Check if users have profile data:
   ```python
   user.objectifs_personnels  # Should not be empty
   user.centres_interet       # Should not be empty
   user.humeur_generale       # Should be set
   ```
2. Check similarity threshold:
   - Minimum: 35% (see `SuggestionConnexionService.MIN_SIMILARITY_SCORE`)
3. Run `test_suggestion_logic` to verify calculation works

### **Djongo/MongoDB errors?**
- The service filters in Python to avoid Djongo compatibility issues
- If errors persist, check MongoDB connection
- Test similarity calculation separately with `test_suggestion_logic`

### **Want to see suggestions immediately?**
```bash
python manage.py clean_test_suggestions
python manage.py create_two_users_test
# Suggestions created with real scores!
```

---

## 📝 Command Summary

| Command | Purpose | Creates Users | Creates Suggestions |
|---------|---------|---------------|---------------------|
| `test_suggestion_logic` | Test algorithm | ✅ (3 users) | ✅ (1 demo) |
| `create_two_users_test` | UI testing | ✅ (Alice & Bob) | ✅ (with real scores) |
| `clean_test_suggestions` | Cleanup | ❌ (deletes) | ❌ (deletes) |
| `create_test_data` | Full test data | ✅ (1 user) | ✅ (if others exist) |

---

**Happy Testing! 🚀**

