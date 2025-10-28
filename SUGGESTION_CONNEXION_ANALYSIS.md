# 🔍 SuggestionConnexion Model Analysis & Logic

## 📋 Current Model Structure

### Model Definition (`communication/models.py`)

```python
class SuggestionConnexion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur_source = models.ForeignKey(CustomUser, related_name='suggestions_envoyees')
    utilisateur_cible = models.ForeignKey(CustomUser, related_name='suggestions_recues')
    
    # Core attributes
    score_similarite = models.FloatField()  # 0.0 to 1.0
    type_suggestion = models.CharField(choices=[
        ('objectif_similaire', 'Objectif similaire'),
        ('humeur_proche', 'Humeur proche'),
        ('interet_commun', 'Intérêt commun'),
    ])
    date_suggestion = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(choices=[
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('ignoree', 'Ignorée'),
    ])
    
    unique_together = ['utilisateur_source', 'utilisateur_cible']
```

---

## 🔴 Current Implementation (PROBLEMS)

### 1. **Simple Generation Logic** (`_generer_suggestions_simples`)

**Current Issues:**
- ❌ Only compares journal count (very basic!)
- ❌ Always uses `type_suggestion='objectif_similaire'` (wrong!)
- ❌ Only suggests 5 users maximum
- ❌ Similarity score calculation is too simple
- ❌ Doesn't check user profile attributes (objectifs, humeur, intérêts)

**Current Code:**
```python
def _generer_suggestions_simples(self, user):
    # Gets users with journals
    other_users = User.objects.exclude(id=user.id).filter(
        journal__isnull=False
    ).distinct()[:5]
    
    for other_user in other_users:
        # Simple count-based similarity
        user_journal_count = Journal.objects.filter(utilisateur=user).count()
        other_journal_count = Journal.objects.filter(utilisateur=other_user).count()
        
        similarity_score = min(user_journal_count, other_journal_count) / max(
            user_journal_count, other_journal_count, 1
        )
        
        if similarity_score > 0.3:
            SuggestionConnexion.objects.create(
                utilisateur_source=user,
                utilisateur_cible=other_user,
                score_similarite=similarity_score,
                type_suggestion='objectif_similaire'  # ALWAYS THE SAME!
            )
```

---

## ✅ What We SHOULD Implement (Based on UML Diagram)

According to the UML diagram, `SuggestionConnexion` should analyze:

### **1. Objectifs Similaires** (`objectif_similaire`)
Compare `objectifs_personnels` (JSONField) between users:
- Calculate Jaccard similarity on objectives lists
- Score > 0.5 = suggest connection

### **2. Humeur Proche** (`humeur_proche`)
Compare `humeur_generale` (enum) between users:
- Same mood = high score (1.0)
- Similar moods (e.g., both positive/negative) = medium score (0.7)
- Different moods = low score (0.3)

### **3. Intérêt Commun** (`interet_commun`)
Compare `centres_interet` (JSONField) between users:
- Calculate Jaccard similarity on interests lists
- Score > 0.4 = suggest connection

---

## 🎯 Proposed Enhanced Logic

### **Similarity Scoring System**

```python
def calculate_similarity_score(user1, user2):
    """
    Calculate comprehensive similarity score based on:
    1. Objectifs personnels (40% weight)
    2. Centres d'intérêt (35% weight)
    3. Humeur générale (15% weight)
    4. Autres facteurs (10% weight: profession, passions, etc.)
    """
    
    scores = {}
    
    # 1. OBJECTIFS SIMILAIRES (40% weight)
    obj1 = set(user1.objectifs_personnels or [])
    obj2 = set(user2.objectifs_personnels or [])
    if obj1 and obj2:
        jaccard_obj = len(obj1 & obj2) / len(obj1 | obj2) if (obj1 | obj2) else 0
        scores['objectif_similaire'] = jaccard_obj
    
    # 2. CENTRES D'INTÉRÊT (35% weight)
    int1 = set(user1.centres_interet or [])
    int2 = set(user2.centres_interet or [])
    if int1 and int2:
        jaccard_int = len(int1 & int2) / len(int1 | int2) if (int1 | int2) else 0
        scores['interet_commun'] = jaccard_int
    
    # 3. HUMEUR GÉNÉRALE (15% weight)
    humeur1 = user1.humeur_generale
    humeur2 = user2.humeur_generale
    if humeur1 and humeur2:
        if humeur1 == humeur2:
            scores['humeur_proche'] = 1.0
        elif (humeur1 in ['heureux', 'neutre'] and humeur2 in ['heureux', 'neutre']) or \
             (humeur1 in ['triste', 'anxieux', 'stresse'] and humeur2 in ['triste', 'anxieux', 'stresse']):
            scores['humeur_proche'] = 0.7
        else:
            scores['humeur_proche'] = 0.3
    
    # 4. AUTRES FACTEURS (10% weight)
    other_score = 0.0
    if user1.profession and user2.profession and user1.profession == user2.profession:
        other_score += 0.3
    if user1.passions and user2.passions:
        passions1 = set(user1.passions or [])
        passions2 = set(user2.passions or [])
        if passions1 and passions2:
            jaccard_passions = len(passions1 & passions2) / len(passions1 | passions2)
            other_score += jaccard_passions * 0.7
    
    scores['other'] = min(other_score, 1.0)
    
    # CALCULATE WEIGHTED OVERALL SCORE
    weights = {
        'objectif_similaire': 0.40,
        'interet_commun': 0.35,
        'humeur_proche': 0.15,
        'other': 0.10
    }
    
    total_score = 0.0
    total_weight = 0.0
    
    for key, score in scores.items():
        if key in weights:
            total_score += score * weights[key]
            total_weight += weights[key]
    
    overall_score = total_score / total_weight if total_weight > 0 else 0.0
    
    # DETERMINE PRIMARY TYPE
    primary_type = 'objectif_similaire'  # default
    if 'interet_commun' in scores and scores['interet_commun'] > scores.get('objectif_similaire', 0):
        primary_type = 'interet_commun'
    elif 'humeur_proche' in scores and scores['humeur_proche'] > 0.8:
        primary_type = 'humeur_proche'
    
    return {
        'overall_score': overall_score,
        'type': primary_type,
        'detailed_scores': scores
    }
```

---

## 📊 Suggested Implementation Structure

### **Service Layer** (`communication/services/suggestion_service.py`)

```python
class SuggestionConnexionService:
    """
    Service for generating and managing connection suggestions
    """
    
    MIN_SIMILARITY_SCORE = 0.35  # Minimum threshold
    MAX_SUGGESTIONS_PER_USER = 10
    
    @staticmethod
    def generate_suggestions_for_user(user, max_suggestions=None):
        """
        Generate connection suggestions for a user based on profile similarity
        """
        # Get all other users (excluding current user and existing suggestions)
        # Calculate similarity for each
        # Create SuggestionConnexion objects
        pass
    
    @staticmethod
    def calculate_similarity(user1, user2):
        """
        Calculate detailed similarity metrics between two users
        """
        pass
    
    @staticmethod
    def get_suggestions_for_user(user, status=None, limit=None):
        """
        Get existing suggestions for a user
        """
        pass
```

---

## 🔧 Next Steps

1. **Create Service File**: `communication/services/suggestion_service.py`
2. **Implement Enhanced Similarity Logic**: Use user profile fields
3. **Update View Logic**: Replace `_generer_suggestions_simples` with service calls
4. **Add Background Task**: Auto-generate suggestions periodically
5. **Add Tests**: Unit tests for similarity calculations

---

## 📝 Notes

- The model structure is CORRECT ✅
- The generation logic is TOO SIMPLE ❌
- Need to use CustomUser fields: `objectifs_personnels`, `centres_interet`, `humeur_generale`
- Should respect `unique_together` constraint
- Should handle bidirectional suggestions properly

