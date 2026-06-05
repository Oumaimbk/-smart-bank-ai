# Captures d'écran à réaliser — Smart Bank AI

Avant de compiler le rapport, placer toutes les images dans le dossier `report/images/`.

**Prérequis :** lancer l'application (`docker compose up`) et importer
`data/reference/transactions_complete_profile.csv` pour avoir des données réelles.

---

## Captures de l'interface (application en cours d'exécution)

### 1. `logo_insea.png`
- **Où :** Site officiel de l'INSEA ou document institutionnel
- **Ce qui doit apparaître :** Logo officiel de l'INSEA (fond blanc ou transparent)
- **Largeur recommandée :** 400px minimum
- **Note :** Utilisé sur la page de garde du rapport

---

### 2. `page_login.png`
- **Où :** `http://localhost:3000/login`
- **Ce qui doit apparaître :**
  - Formulaire de connexion avec champs Email et Mot de passe
  - Bouton "Se connecter"
  - Lien vers la page d'inscription
  - Interface propre et centrée
- **Résolution recommandée :** 1280×800

---

### 3. `page_dashboard.png`
- **Où :** `http://localhost:3000/` ou `/dashboard` (après login et import CSV)
- **Ce qui doit apparaître :**
  - Les 4 KPI cards : Total dépenses, Total revenus, Épargne nette, Nombre de transactions
  - Graphique camembert (PieChart) des dépenses par catégorie avec légende
  - Graphique en barres (BarChart) de l'évolution mensuelle
  - Barre latérale de navigation visible
- **Note :** S'assurer que les données sont chargées (importer le CSV avant)

---

### 4. `page_upload.png`
- **Où :** `http://localhost:3000/upload`
- **Ce qui doit apparaître :**
  - Zone de dépôt de fichier CSV (bouton ou zone drag & drop)
  - Résultats du dernier import affiché :
    - Nombre de nouvelles transactions
    - Nombre de doublons ignorés
    - Nombre d'anomalies détectées
    - Nombre de recommandations générées
  - Tableau historique des imports précédents avec colonnes : fichier, date, nb transactions, bouton supprimer
- **Note :** Prendre la capture après un import réussi

---

### 5. `page_transactions.png`
- **Où :** `http://localhost:3000/transactions`
- **Ce qui doit apparaître :**
  - Tableau paginé des transactions avec colonnes :
    Date, Montant, Direction (Débit/Crédit), Libellé, Commerçant, Catégorie, Confiance
  - Badges colorés pour les catégories (chaque catégorie a sa couleur)
  - Filtres visibles (par direction, recherche texte)
  - Pagination en bas du tableau
- **Note :** Filtrer sur "Debit" pour montrer les dépenses uniquement

---

### 6. `page_anomalies.png`
- **Où :** `http://localhost:3000/anomalies`
- **Ce qui doit apparaître :**
  - Liste des transactions suspectes détectées
  - Pour chaque anomalie : date, montant, libellé, type d'anomalie
    (ex. "Montant élevé", "Heure inhabituelle", "Isolation Forest")
  - Score d'anomalie affiché
  - Si possible, badges colorés selon le type d'anomalie
- **Note :** Les données doivent venir du CSV importé

---

### 7. `page_recommandations.png`
- **Où :** `http://localhost:3000/recommendations`
- **Ce qui doit apparaître :**
  - Cartes de recommandations budgétaires (au moins 3 visibles)
  - Chaque carte avec : type (warning / tip / alert), message en français, catégorie concernée
  - Section prévisions du mois prochain (tableau ou barres par catégorie)
- **Note :** Les recommandations sont générées automatiquement après l'import CSV

---

### 8. `page_ai_insights.png`
- **Où :** `http://localhost:3000/ai-insights`
- **Ce qui doit apparaître :**
  - Métriques du modèle de catégorisation (Accuracy 99.6%, F1 0.9963...)
  - Métriques du Random Forest (R² 0.98, MAE, RMSE)
  - Graphique d'importance des features ou distribution des catégories
  - Informations sur l'Isolation Forest (contamination, nb estimateurs)
- **Note :** Ces métriques viennent du endpoint `/api/analytics/ml-metrics/`

---

## Diagrammes à créer (outil de modélisation UML)

Utiliser **draw.io** (gratuit, en ligne sur `https://app.diagrams.net`)
ou **StarUML**, **Lucidchart**, **PlantUML**.

---

### 9. `diagramme_usecase.png`
- **Type :** Diagramme UML de cas d'utilisation
- **Acteurs :**
  - Acteur principal "Utilisateur" (à gauche)
- **Cas d'utilisation (ellipses) :**
  - S'inscrire
  - Se connecter / Se déconnecter
  - Importer un fichier CSV
  - Consulter le tableau de bord
  - Consulter les transactions (inclut : Filtrer, Rechercher)
  - Consulter les anomalies
  - Consulter les recommandations
  - Consulter les prévisions
  - Supprimer un lot d'import
- **Relations :** "Consulter les transactions" <<include>> "Filtrer les transactions"
- **Cadre :** Système "Smart Bank AI"

---

### 10. `diagramme_classes.png`
- **Type :** Diagramme UML de classes
- **Classes et attributs :**
  ```
  User
  - id: int (PK)
  - username: str
  - email: str (unique)
  - password: str (hashé)
  - date_joined: datetime

  UploadBatch
  - id: int (PK)
  - user: FK→User
  - filename: str
  - created_at: datetime
  - transaction_count: int

  Transaction
  - id: int (PK)
  - user: FK→User
  - batch: FK→UploadBatch
  - transaction_id: str (unique/user)
  - transaction_date: date
  - direction: str (Debit/Credit)
  - amount: decimal
  - narration: str
  - merchant_name: str
  - category: str
  - category_confidence: float

  Anomaly
  - id: int (PK)
  - transaction: FK→Transaction
  - anomaly_type: str
  - score: float
  - details: JSON

  Recommendation
  - id: int (PK)
  - user: FK→User
  - rec_type: str
  - message: str
  - priority: int
  - category: str
  - created_at: datetime

  Prediction
  - id: int (PK)
  - user: FK→User
  - category: str
  - predicted_amount: decimal
  - month: str
  ```
- **Relations :**
  - User 1 ——< UploadBatch (one-to-many)
  - User 1 ——< Transaction (one-to-many)
  - UploadBatch 1 ——< Transaction (one-to-many)
  - Transaction 1 ——< Anomaly (one-to-many)
  - User 1 ——< Recommendation (one-to-many)
  - User 1 ——< Prediction (one-to-many)

---

### 11. `diagramme_sequence.png`
- **Type :** Diagramme UML de séquence
- **Titre :** Import CSV et traitement ML
- **Participants (de gauche à droite) :**
  - :Utilisateur
  - :Frontend (React)
  - :API (Django)
  - :PipelineService
  - :ML Pipeline
  - :PostgreSQL
- **Séquence :**
  1. Utilisateur → Frontend : sélectionne fichier CSV
  2. Frontend → API : POST /api/transactions/upload/ [Bearer JWT]
  3. API → API : valide JWT (SimpleJWT)
  4. API → PipelineService : run(file, user)
  5. PipelineService → ML Pipeline : load_csv() → clean() → classify()
  6. ML Pipeline → ML Pipeline : detect_anomalies() → predict() → recommend()
  7. ML Pipeline → PipelineService : résultats
  8. PipelineService → PostgreSQL : bulk_create(transactions, anomalies, recommendations)
  9. API → Frontend : 201 {new_transactions, anomalies_detected, ...}
  10. Frontend → Utilisateur : affiche résultats de l'import

---

### 12. `architecture_3couches.png`
- **Type :** Schéma architectural (boîtes et flèches)
- **Structure à représenter :**
  ```
  ┌─────────────────────────────────────────┐
  │           Docker Compose                │
  │  ┌──────────────┐  ┌────────────────┐   │
  │  │  Frontend    │  │   Backend      │   │
  │  │  React/Vite  │→ │  Django REST   │   │
  │  │  (port 3000) │  │  Framework     │   │
  │  │  - Dashboard │  │  (port 8000)   │   │
  │  │  - Upload    │  │  ┌──────────┐  │   │
  │  │  - Anomalies │  │  │ Services │  │   │
  │  │  - Recos     │  │  │  Layer   │  │   │
  │  └──────────────┘  │  └────┬─────┘  │   │
  │                    │       │        │   │
  │                    │  ┌────▼─────┐  │   │
  │                    │  │    ML    │  │   │
  │                    │  │ Pipeline │  │   │
  │                    │  │ TF-IDF   │  │   │
  │                    │  │ IForest  │  │   │
  │                    │  │ RF       │  │   │
  │                    │  └──────────┘  │   │
  │                    └───────┬────────┘   │
  │  ┌──────────────────────────▼────────┐  │
  │  │        PostgreSQL (port 5432)     │  │
  │  └───────────────────────────────────┘  │
  └─────────────────────────────────────────┘
  ```

---

### 13. `architecture_docker.png`
- **Type :** Schéma Docker Compose
- **Représenter les 3 services avec leurs propriétés :**
  - `db` : image postgres:15-alpine, port 5432, volume postgres_data, health check
  - `backend` : Python 3.11, port 8000, bind mount ./backend:/app, depends_on db
  - `frontend` : node:20-alpine, port 3000, volume frontend_node_modules, depends_on backend
- **Flèches :** frontend → backend (proxy /api), backend → db (ORM)

---

### 14. `mld_base_donnees.png`
- **Type :** Schéma MLD (Modèle Logique des Données)
- **Tables avec clés primaires/étrangères** (voir description dans le rapport chapitre 3)
- Utiliser les conventions MLD : souligner les PK, indiquer les FK avec flèches

---

### 15. `pipeline_ml.png`
- **Type :** Schéma de pipeline (flèches horizontales)
- **Étapes en boîtes colorées :**
  ```
  [CSV brut] → [Nettoyage & Validation] → [Feature Engineering]
  → [TF-IDF + LR (Catégorisation)] → [Isolation Forest (Anomalies)]
  → [Random Forest (Prévisions)] → [Moteur Recommandations] → [PostgreSQL]
  ```
- **Couleurs suggérées :** bleu pour entrée/sortie, vert pour ML, orange pour règles

---

## Fichiers déjà disponibles dans `backend/models_store/`
Ces images existent déjà — les copier directement dans `report/images/` :

### 16. `matrice_confusion.png`
- **Source :** `backend/models_store/confusion_matrix_classification.png`
- Copier et renommer en `matrice_confusion.png`

### 17. `f1_par_categorie.png`
- **Source :** `backend/models_store/f1_per_category.png`
- Copier et renommer en `f1_par_categorie.png`

### 18. `isolation_forest_viz.png`
- **Source :** `backend/models_store/isolation_forest_visualization.png`
- Copier et renommer en `isolation_forest_viz.png`

### 19. `importance_features_rf.png`
- **Source :** `backend/models_store/top_features_per_category.png`
- Copier et renommer en `importance_features_rf.png`

### 20. `prediction_vs_reel.png`
- **Source :** `backend/models_store/prediction_actual_vs_predicted.png`
- Copier et renommer en `prediction_vs_reel.png`

---

## Récapitulatif des fichiers attendus dans `report/images/`

| # | Fichier | Source | Action |
|---|---------|--------|--------|
| 1 | `logo_insea.png` | Site INSEA | Télécharger |
| 2 | `page_login.png` | localhost:3000/login | Screenshot |
| 3 | `page_dashboard.png` | localhost:3000/ | Screenshot |
| 4 | `page_upload.png` | localhost:3000/upload | Screenshot |
| 5 | `page_transactions.png` | localhost:3000/transactions | Screenshot |
| 6 | `page_anomalies.png` | localhost:3000/anomalies | Screenshot |
| 7 | `page_recommandations.png` | localhost:3000/recommendations | Screenshot |
| 8 | `page_ai_insights.png` | localhost:3000/ai-insights | Screenshot |
| 9 | `diagramme_usecase.png` | draw.io | Créer |
| 10 | `diagramme_classes.png` | draw.io | Créer |
| 11 | `diagramme_sequence.png` | draw.io | Créer |
| 12 | `architecture_3couches.png` | draw.io | Créer |
| 13 | `architecture_docker.png` | draw.io | Créer |
| 14 | `mld_base_donnees.png` | draw.io | Créer |
| 15 | `pipeline_ml.png` | draw.io | Créer |
| 16 | `matrice_confusion.png` | models_store/ | Copier+renommer |
| 17 | `f1_par_categorie.png` | models_store/ | Copier+renommer |
| 18 | `isolation_forest_viz.png` | models_store/ | Copier+renommer |
| 19 | `importance_features_rf.png` | models_store/ | Copier+renommer |
| 20 | `prediction_vs_reel.png` | models_store/ | Copier+renommer |

---

## Commandes utiles pour copier les images existantes

```bash
# Depuis le dossier PE/PE/
cp backend/models_store/confusion_matrix_classification.png report/images/matrice_confusion.png
cp backend/models_store/f1_per_category.png                 report/images/f1_par_categorie.png
cp backend/models_store/isolation_forest_visualization.png  report/images/isolation_forest_viz.png
cp backend/models_store/top_features_per_category.png       report/images/importance_features_rf.png
cp backend/models_store/prediction_actual_vs_predicted.png  report/images/prediction_vs_reel.png
```
