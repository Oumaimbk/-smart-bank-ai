# Smart Bank AI — Analyseur Intelligent de Transactions Bancaires

> Application web full-stack d'analyse de transactions bancaires marocaines par intelligence artificielle.  
> Upload CSV → catégorisation ML → détection d'anomalies → prévisions → recommandations → métriques d'évaluation.

---

## Table des matières

1. [Description du projet](#1-description-du-projet)
2. [Fonctionnalités](#2-fonctionnalités)
3. [Architecture technique](#3-architecture-technique)
4. [Stack technologique](#4-stack-technologique)
5. [Pipeline ML — les 3 modèles](#5-pipeline-ml--les-3-modèles)
6. [Évaluation des modèles — AI Insights](#6-évaluation-des-modèles--ai-insights)
7. [Détection d'anomalies — double méthode](#7-détection-danomalies--double-méthode)
8. [Recommandations enrichies](#8-recommandations-enrichies)
9. [Flux de traitement](#9-flux-de-traitement)
10. [Modèle de données](#10-modèle-de-données)
11. [Lancer le projet](#11-lancer-le-projet)
12. [Variables d'environnement](#12-variables-denvironnement)
13. [Endpoints API](#13-endpoints-api)
14. [Format du fichier CSV](#14-format-du-fichier-csv)
15. [Tests](#15-tests)
16. [Comment tester les nouvelles fonctionnalités AI](#16-comment-tester-les-nouvelles-fonctionnalités-ai)
17. [Structure du projet](#17-structure-du-projet)

---

## 1. Description du projet

**Smart Bank AI** est une application web développée dans le cadre d'un projet de fin d'études (PFA). Elle permet à un utilisateur d'importer ses relevés bancaires au format CSV, puis d'obtenir automatiquement :

- Une **catégorisation** de chaque transaction (Alimentation, Transport, Logement, etc.) grâce à un modèle TF-IDF + Régression Logistique.
- Une **détection de schémas de dépenses inhabituels** par deux méthodes simultanées : Isolation Forest (ML) + règles statistiques (z-score, horaires).
- Des **prévisions de dépenses** pour le mois suivant par catégorie, calculées par un Random Forest Regressor.
- Des **recommandations budgétaires** personnalisées, enrichies par les données d'anomalies et une explication détaillée de chaque conseil.
- Un tableau de bord **AI Insights** avec métriques d'évaluation des modèles (MAE, RMSE, R², accuracy, F1) et importance des variables.

Le dataset d'entraînement est un ensemble de **57 382 transactions** (46 702 originales + 10 680 nouvelles) couvrant **14 catégories** dont des marchands internationaux (H&M, Nike, Zara, Amazon, AliExpress, Jumia, Fnac, Sephora…).

---

## 2. Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| Authentification JWT | Inscription, connexion, refresh token, isolation des données par utilisateur |
| Import CSV | Upload jusqu'à 10 Mo, validation des colonnes, déduplication automatique |
| Catégorisation ML | TF-IDF + Logistic Regression — 11 catégories, accuracy 100 % sur données synthétiques |
| Détection d'anomalies | **Double méthode simultanée** : Isolation Forest (`ml_isolation_forest`) + règles z-score/horaire (`rule_high_amount`, `rule_odd_hour`) |
| Prévisions budgétaires | Random Forest Regressor (200 arbres, 6 features) — ré-entraîné à chaque upload |
| Recommandations enrichies | Basées sur prévisions + anomalies par catégorie + fort volume, avec champ `reason` explicatif |
| Tableau de bord | KPIs, évolution mensuelle, top marchands, dépenses par catégorie |
| **AI Insights** | Métriques d'évaluation (MAE, RMSE, R², accuracy, F1), importance des variables (bar chart), explication des méthodes |
| **Suppression de batch** | Corbeille rouge dans l'historique des imports — supprime toutes les transactions liées |
| Multi-utilisateurs | Chaque utilisateur voit uniquement ses propres données |
| API REST | Tous les endpoints protégés par JWT, pagination intégrée |

---

## 3. Architecture technique

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│    React 18 + Vite · React Router · Recharts (bar/line/pie)     │
│    Pages: Dashboard · Upload · Transactions · Anomalies         │
│           Recommandations · AI Insights (NEW)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │  HTTP REST + JWT Bearer
┌────────────────────────────▼─────────────────────────────────────┐
│                        API LAYER                                 │
│                  Django REST Framework                           │
│   accounts · transactions · analytics · anomalies               │
│   recommendations · (ml-metrics NEW) · (feature-importance NEW) │
│              JWT Auth · IsAuthenticated · Pagination            │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      SERVICE LAYER                               │
│   PipelineService.run()  (orchestration atomique, 10 étapes)    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                  ML PIPELINE (mis à jour)                        │
│  Ingestion → Nettoyage → Catégorisation (TF-IDF + LR)           │
│  → Anomalies (IF + règles, simultané)                           │
│  → Ré-entraînement RF + sauvegarde métriques (NEW)              │
│  → Prédictions → Recommandations enrichies (NEW)                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    PERSISTENCE                                   │
│   PostgreSQL 15 : users · transactions · batches · anomalies    │
│                   predictions · recommendations · ml_model_metrics (NEW) │
│   models_store/ : tfidf_vectorizer.pkl · lr_category_classifier.pkl │
│                   isolation_forest.pkl · anomaly_label_encoder.pkl  │
│                   rf_expense_predictor.pkl · category_encoder.pkl   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Stack technologique

| Couche | Technologie | Version | Rôle |
|---|---|---|---|
| Backend | Django | 4.2 | Framework web principal |
| API | Django REST Framework | 3.15 | Sérialisation, vues, pagination |
| Auth | djangorestframework-simplejwt | 5.3 | Tokens JWT (access + refresh) |
| CORS | django-cors-headers | 4.3 | Autorise les requêtes React → Django |
| Base de données | PostgreSQL | 15 | Stockage relationnel |
| Driver BDD | psycopg2-binary | 2.9 | Connecteur Python ↔ PostgreSQL |
| Config | python-decouple | 3.8 | Variables d'environnement (.env) |
| ML — vectorisation | scikit-learn TfidfVectorizer | 1.4 | Transformation texte en features |
| ML — classification | scikit-learn LogisticRegression | 1.4 | Catégorisation des transactions |
| ML — anomalies | scikit-learn IsolationForest | 1.4 | Détection non supervisée |
| ML — prévision | scikit-learn RandomForestRegressor | 1.4 | Prédiction + métriques + importances |
| ML — évaluation | sklearn.metrics | 1.4 | MAE, RMSE, R², accuracy, F1 |
| Dataframes | pandas | 2.1 | Traitement CSV et features |
| Sérialisation ML | joblib | 1.4 | Sauvegarde/chargement des .pkl |
| Frontend | React | 18 | Interface utilisateur |
| Build | Vite | 5.4 | Bundler + dev server |
| Routing | React Router DOM | — | Navigation SPA |
| Graphiques | Recharts | — | Bar chart, line chart, pie chart |
| HTTP client | Axios | — | Appels vers l'API REST |
| Icônes | react-icons | — | Icônes UI |
| Containerisation | Docker + Docker Compose | — | Orchestration des 3 services |

---

## 5. Pipeline ML — les 3 modèles

### 5.1 TF-IDF + Régression Logistique — Catégorisation

**Objectif** : assigner automatiquement une catégorie à chaque transaction à partir de son libellé et du nom du marchand.

**Pipeline** :
```
text_to_segment = clean_merchant_name + ' ' + clean_narration (minuscules)
      │
      ▼
TfidfVectorizer(ngram_range=(1,2), max_features=10 000)
      │
      ▼
LogisticRegression(max_iter=1000, C=5, multi_class='multinomial')
      │
      ▼
category  +  category_confidence
```

**11 catégories** : Alimentation · E-commerce · Factures · Logement · Loisirs · Retrait cash · Revenu · Santé · Shopping · Transport · Voyage

**Fallback** : si les fichiers `.pkl` sont absents, un classifieur par règles (mots-clés) prend le relais.

**Métriques évaluées** (sur holdout 20 %) :

| Métrique | Score |
|---|---|
| Accuracy | 100.00 % |
| F1 (weighted) | 1.0000 |
| F1 (macro) | 1.0000 |
| Précision | 1.0000 |
| Rappel | 1.0000 |

---

### 5.2 Isolation Forest + Règles — Détection d'anomalies

Voir section 7 pour le détail complet de la double méthode.

---

### 5.3 Random Forest Regressor — Prévision mensuelle

**Objectif** : prédire le montant total dépensé par catégorie pour le mois suivant.

**Features (6)** :

| Feature | Description |
|---|---|
| `Montant moyen` | Montant moyen par transaction (MAD) |
| `Nb transactions` | Nombre de transactions ce mois-ci |
| `Période` | Numéro de période année × 12 + mois (tendance temporelle) |
| `Mois` | Numéro du mois 1–12 (saisonnalité) |
| `Catégorie` | Catégorie encodée numériquement (LabelEncoder) |
| `Ratio week-end` | Proportion de transactions le week-end |

**Hyperparamètres** :
```python
RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_leaf=2, random_state=42, n_jobs=-1)
```

**Évaluation** : à chaque upload CSV, le modèle est **ré-entraîné** sur toutes les données de l'utilisateur avec un **holdout 80/20**. Les métriques (MAE, RMSE, R²) et les importances de variables sont sauvegardées en base de données et exposées via l'API.

---

## 6. Évaluation des modèles — AI Insights

### Nouvelles métriques stockées en base

À chaque ré-entraînement du Random Forest, les métriques suivantes sont calculées sur un **holdout 20 %** et persistées dans la table `ml_model_metrics` :

| Modèle | Métriques stockées |
|---|---|
| Random Forest Regressor | MAE (MAD), RMSE (MAD), R² |
| TF-IDF + Logistic Regression | Accuracy, F1 (weighted), F1 (macro), Précision, Rappel |

### Importance des variables

Le Random Forest expose nativement l'importance de chaque feature via `model.feature_importances_`. Ces valeurs sont sauvegardées avec les métriques et affichées sous forme de **bar chart horizontal** dans l'interface.

Exemple de résultat typique sur le dataset de 46 702 transactions :

| Rang | Variable | Importance |
|---|---|---|
| 1 | Montant moyen | ~94 % |
| 2 | Nb transactions | ~5 % |
| 3 | Catégorie | ~1 % |
| 4–6 | Période, Mois, Ratio week-end | < 1 % |

### API dédiée

```
GET /api/analytics/ml-metrics/           → métriques MAE, RMSE, R², accuracy, F1
GET /api/analytics/feature-importance/   → importances par variable, rang, %
```

### Page AI Insights (frontend)

Accessible via la sidebar → **AI Insights** (`/ai-insights`), la page affiche :
- Diagramme du pipeline ML (4 étapes)
- Cartes de métriques par modèle
- Bar chart d'importance des variables
- Explication des méthodes de détection d'anomalies

---

## 7. Détection d'anomalies — double méthode

Depuis la dernière mise à jour, les **deux méthodes s'exécutent simultanément** sur chaque upload CSV. Une transaction peut être flaggée par l'une ou l'autre (ou les deux) avec des types distincts.

### Méthode 1 — Isolation Forest (ML)

```python
IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
```

- **Features** : montant, heure, week-end, catégorie encodée
- **Type stocké** : `ml_isolation_forest`
- **Description** : "Isolation Forest a identifié cette transaction comme un schéma de dépense inhabituel"

### Méthode 2 — Règles statistiques

| Règle | Condition | Type stocké |
|---|---|---|
| Montant élevé | z-score > 2.5 dans la catégorie | `rule_high_amount` |
| Heure suspecte | Transaction entre 00h00 et 05h59 | `rule_odd_hour` |

### Types d'anomalies — tableau complet

| Type | Source | Description affichée |
|---|---|---|
| `ml_isolation_forest` | Isolation Forest | Schéma inhabituel (IF) |
| `rule_high_amount` | Règle z-score | Montant élevé (règle) |
| `rule_odd_hour` | Règle horaire | Heure suspecte (règle) |

---

## 8. Recommandations enrichies

### Signaux utilisés

Les recommandations combinent désormais trois signaux :

| Signal | Condition | Priorité |
|---|---|---|
| Prévision RF : forte hausse | > +50 % vs moyenne | **haute** |
| Prévision RF : hausse modérée | > +20 % vs moyenne | **moyenne** |
| Fort volume de dépense | Moyenne > 1 500 MAD/mois | **basse** |
| Anomalies dans la catégorie | ≥ 3 flags | **haute** |
| Anomalies dans la catégorie | 1–2 flags | **moyenne** |

### Champ `reason`

Chaque recommandation inclut maintenant un champ `reason` qui cite les données précises ayant déclenché le conseil :

```json
{
  "category": "Alimentation",
  "message": "Vos dépenses en Alimentation sont prévues en hausse de 67 % ...",
  "reason": "Prévision Random Forest : 4 200 MAD (+67 % vs moyenne 2 510 MAD/mois sur 12 mois).",
  "priority": "high"
}
```

Ce champ est affiché en italique sous le message dans la page Recommandations.

---

## 9. Flux de traitement

Lors de chaque upload de fichier CSV, `PipelineService.run()` exécute les étapes suivantes de façon atomique :

```
Fichier CSV reçu
        │
        ▼
1. Ingestion      load_csv() + validate_columns()
        │           Colonnes requises : transaction_id, transaction_date, direction, amount
        ▼
2. Nettoyage      clean()
        │           Doublons, dates, montants, direction (Credit/Debit)
        ▼
3. Normalisation  normalize() + engineer_features()
        │           text_to_segment, hour, is_weekend, narration_normalized
        ▼
4. Catégorisation classify()  → TF-IDF + LR
        │           Ajoute : category, category_confidence
        ▼
5. Déduplication  Ignore les transaction_id déjà en base pour cet utilisateur
        │
        ▼
6. Sauvegarde     Transaction.objects.bulk_create()
        │
        ▼
7. Anomalies      detect() = _ml_detect() + _rule_detect() (simultané)
        │           Types : ml_isolation_forest / rule_high_amount / rule_odd_hour
        │           Calcule anomaly_summary par catégorie → passé aux recommandations
        ▼
8. Ré-entraînement train() → Random Forest sur toutes les données de l'utilisateur
        │           Évalue sur holdout 20 % → sauvegarde MAE/RMSE/R² + feature importances
        │           dans ml_model_metrics (update_or_create)
        ▼
9. Prédictions    predict_next_month()
        │           Prediction.objects.bulk_create()
        ▼
10. Recommandations generate(df, predictions, anomaly_summary)
        │           Règles sur prévisions + anomalies + volumes
        │           Chaque recommandation : message + reason + priority
        ▼
Réponse JSON : { batch_id, new_transactions, skipped_duplicates,
                 anomalies_detected, predictions_generated,
                 recommendations_generated }
```

---

## 10. Modèle de données

```
┌─────────────────────────────────────────────┐
│                   User                      │
│  id · username · email · date_joined        │
└───────────┬─────────────────────────────────┘
            │ 1:N
┌───────────▼──────────┐  ┌──────────────────────────────────────────────┐
│    UploadBatch       │  │                 Transaction                  │
│  id · filename       │  │  id · transaction_id · customer_id           │
│  status              │  │  transaction_date · transaction_time         │
│  transaction_count   │  │  account_type · payment_method              │
│  error_message       │  │  direction (Credit/Debit)                   │
│  created_at          │  │  amount · balance_after                     │
│  processed_at        │  │  narration · merchant_name                  │
└──────────────────────┘  │  merchant_city · merchant_country           │
                          │  category · created_at                      │
                          └────────────────┬─────────────────────────────┘
                                           │ 1:N
                          ┌────────────────▼─────────────────────────────┐
                          │                 Anomaly                      │
                          │  id · anomaly_type · score · description     │
                          │  Types: ml_isolation_forest                  │
                          │         rule_high_amount                    │
                          │         rule_odd_hour                       │
                          └──────────────────────────────────────────────┘

┌───────────────────────────────────┐  ┌──────────────────────────────────────┐
│           Prediction              │  │           Recommendation              │
│  category · target_period         │  │  category · message                  │
│  predicted_amount                 │  │  reason (NEW)                        │
│  [unique: user+category+period]   │  │  priority (high/medium/low)          │
└───────────────────────────────────┘  └──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   MLModelMetrics (NEW)                   │
│  model_name (unique) : 'random_forest'                   │
│                        'logistic_regression'             │
│  metrics   : { mae, rmse, r2 }  ou  { accuracy, f1... } │
│  feature_importance : [ {feature, importance, rank} ]   │
│  sample_count · computed_at                             │
└──────────────────────────────────────────────────────────┘
```

---

## 11. Lancer le projet

### Prérequis
- Docker Desktop installé et **démarré**

### Installation

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd PE

# 2. Créer le fichier d'environnement
cp .env.example .env

# 3. Démarrer tous les services en arrière-plan
docker compose up -d --build

# 4. Si vous venez d'ajouter des migrations (après un git pull par exemple)
docker exec pe-backend-1 python manage.py migrate
```

| Service | URL |
|---|---|
| Application React | http://localhost:3000 |
| API Django REST | http://localhost:8000 |
| Interface Admin Django | http://localhost:8000/admin/ |

### Commandes utiles

```bash
docker compose logs -f              # Logs en temps réel
docker compose logs -f backend      # Logs backend uniquement
docker compose ps                   # État des conteneurs
docker compose down                 # Arrêter (données conservées)
docker compose down -v              # Arrêter + supprimer volumes (reset BDD)
docker exec -it pe-backend-1 sh     # Shell dans le conteneur backend
docker exec pe-backend-1 python manage.py migrate        # Appliquer migrations
docker exec pe-backend-1 python manage.py createsuperuser
```

### Tests (sans Docker)

```bash
cd backend
python -m pytest tests/ -v
# → 63 passed
```

---

## 12. Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | Settings Django |
| `SECRET_KEY` | `change-me-...` | Clé secrète — **changer en production** |
| `DEBUG` | `True` | Mode debug |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,backend` | Hôtes autorisés |
| `POSTGRES_DB` | `bank_analyzer` | Nom de la base |
| `POSTGRES_USER` | `bank_user` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | `bank_password` | Mot de passe PostgreSQL |
| `POSTGRES_HOST` | `db` | Hôte PostgreSQL (nom service Docker) |
| `POSTGRES_PORT` | `5432` | Port PostgreSQL |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | Durée token d'accès |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` | Durée token refresh |

---

## 13. Endpoints API
11
### Authentification

| Méthode | URL | Description | Auth |
|---|---|---|:---:|
| `POST` | `/api/auth/register/` | Créer un compte | Non |
| `POST` | `/api/auth/login/` | Connexion → `access` + `refresh` + user | Non |
| `POST` | `/api/auth/token/refresh/` | Rafraîchir le token | Non |
| `GET` | `/api/auth/me/` | Profil utilisateur connecté | Oui |

### Transactions

| Méthode | URL | Description | Auth |
|---|---|---|:---:|
| `POST` | `/api/transactions/upload/` | Import CSV (multipart, champ `file`) | Oui |
| `GET` | `/api/transactions/` | Liste paginée (filtres: direction, category, search) | Oui |
| `GET` | `/api/transactions/batches/` | Historique des imports | Oui |
| `DELETE` | `/api/transactions/batches/<id>/delete/` | **[NEW]** Supprimer un import et toutes ses transactions | Oui |

### Analytics

| Méthode | URL | Description | Auth |
|---|---|---|:---:|
| `GET` | `/api/analytics/kpi/` | KPIs globaux | Oui |
| `GET` | `/api/analytics/spending-by-category/` | Dépenses par catégorie (Debit) | Oui |
| `GET` | `/api/analytics/monthly-evolution/` | Évolution mensuelle débit/crédit | Oui |
| `GET` | `/api/analytics/top-merchants/` | Top 10 marchands | Oui |
| `GET` | `/api/analytics/ml-metrics/` | **[NEW]** Métriques ML (MAE, RMSE, R², accuracy, F1) | Oui |
| `GET` | `/api/analytics/feature-importance/` | **[NEW]** Importances des variables RF | Oui |

### Anomalies

| Méthode | URL | Description | Auth |
|---|---|---|:---:|
| `GET` | `/api/anomalies/` | Liste (paginé, filtre `anomaly_type`) | Oui |
| `GET` | `/api/anomalies/summary/` | Total + répartition par type | Oui |

### Recommandations & Prévisions

| Méthode | URL | Description | Auth |
|---|---|---|:---:|
| `GET` | `/api/recommendations/` | Conseils budgétaires avec champ `reason` **[mis à jour]** | Oui |
| `GET` | `/api/recommendations/predictions/` | Prévisions mois suivant par catégorie | Oui |

---

## 14. Format du fichier CSV

**Colonnes obligatoires** :

| Colonne | Type | Exemple |
|---|---|---|
| `transaction_id` | string | `TX0001` |
| `transaction_date` | date (YYYY-MM-DD) | `2024-01-15` |
| `direction` | `Credit` ou `Debit` | `Debit` |
| `amount` | décimal | `250.00` |

**Colonnes optionnelles** (enrichissent les analyses) :

| Colonne | Exemple |
|---|---|
| `transaction_time` | `14:30` |
| `narration` | `CARREFOUR MARJANE RABAT` |
| `merchant_name` | `Carrefour` |
| `payment_method` | `Carte`, `Virement instantané`, `Wallet` |
| `balance_after` | `9750.00` |
| `merchant_city` | `Rabat` |
| `merchant_country` | `MA` |

**Contraintes** : encodage UTF-8, taille max 10 Mo, doublons sur `transaction_id` ignorés silencieusement.

---

## 15. Tests

**63 tests** au total, tous exécutés avec SQLite en mémoire (pas de Docker nécessaire).

```bash
cd backend
python -m pytest tests/ -v
```

| Fichier | Tests | Ce qui est couvert |
|---|---|---|
| `test_auth.py` | 5 | Register, login, me, rejet sans token |
| `test_transactions.py` | 15 | Upload, déduplication, filtres, isolation utilisateurs, suppression de batch |
| `test_analytics.py` | 8 | KPIs, catégories, évolution, auth requise |
| `test_anomalies.py` | 7 | Liste, summary, filtre, nouveaux types, auth |
| `test_recommendations.py` | 6 | Recommandations + prévisions + champ reason |
| `test_ml_insights.py` | 12 | **[NEW]** Métriques ML, feature importance, types anomalies, reason |
| `test_classifier.py` | 5 | Catégorisation (Transport, Alimentation, Revenu…) |
| `test_cleaner.py` | 5 | Nettoyage CSV (doublons, dates, montants) |

---

## 16. Comment tester les nouvelles fonctionnalités AI

### Prérequis : avoir des données en base
Les nouvelles fonctionnalités (métriques, importances, recommandations enrichies) se calculent lors de l'**upload CSV**. Si vous n'avez pas encore de données :

```bash
# Utiliser le dataset fourni
# Fichier : data/processed/transactions_segmentees.csv (46 702 lignes)
# Ou créer un compte et uploader via l'interface → http://localhost:3000/upload
```

---

### Test 1 — Page AI Insights (frontend)

1. Ouvrez http://localhost:3000
2. Connectez-vous (ou créez un compte)
3. Cliquez sur **AI Insights** dans la sidebar
4. Vous devez voir :
   - Le diagramme pipeline (4 étapes)
   - Les métriques du modèle TF-IDF + LR (accuracy, F1…) si le CSV de référence est disponible
   - Les métriques du Random Forest (MAE, RMSE, R²) après un premier upload
   - Le bar chart d'importance des variables
   - Les deux cartes d'explication des méthodes de détection

---

### Test 2 — Endpoint ml-metrics (API)

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"votre@email.com","password":"VotreMotDePasse"}' \
  | grep -o '"access":"[^"]*"'

# 2. Appeler l'endpoint (remplacer TOKEN)
curl http://localhost:8000/api/analytics/ml-metrics/ \
  -H "Authorization: Bearer TOKEN"
```

**Réponse attendue :**
```json
{
  "models": [
    {
      "model_name": "logistic_regression",
      "display_name": "TF-IDF + Régression Logistique",
      "task": "Catégorisation des transactions",
      "metrics": { "accuracy": 1.0, "f1_weighted": 1.0, "f1_macro": 1.0, "precision": 1.0, "recall": 1.0 },
      "sample_count": 9341
    },
    {
      "model_name": "random_forest",
      "display_name": "Random Forest Regressor",
      "task": "Prévision des dépenses mensuelles",
      "metrics": { "mae": 17127.34, "rmse": 20933.22, "r2": 0.8405 },
      "sample_count": 15
    }
  ]
}
```

---

### Test 3 — Endpoint feature-importance (API)

```bash
curl http://localhost:8000/api/analytics/feature-importance/ \
  -H "Authorization: Bearer TOKEN"
```

**Réponse attendue :**
```json
{
  "features": [
    { "feature": "Montant moyen",    "importance": 0.9441, "rank": 1, "importance_pct": 94.4 },
    { "feature": "Nb transactions",  "importance": 0.0481, "rank": 2, "importance_pct": 4.8 },
    { "feature": "Catégorie",        "importance": 0.0064, "rank": 3, "importance_pct": 0.6 },
    { "feature": "Période",          "importance": 0.0005, "rank": 4, "importance_pct": 0.1 },
    { "feature": "Mois",             "importance": 0.0005, "rank": 5, "importance_pct": 0.1 },
    { "feature": "Ratio week-end",   "importance": 0.0004, "rank": 6, "importance_pct": 0.0 }
  ],
  "model": "Random Forest Regressor"
}
```

---

### Test 4 — Double détection d'anomalies (API)

Après un upload, vérifiez que les deux types d'anomalies coexistent :

```bash
# Tous les types détectés
curl "http://localhost:8000/api/anomalies/summary/" \
  -H "Authorization: Bearer TOKEN"

# Filtrer par type IF uniquement
curl "http://localhost:8000/api/anomalies/?anomaly_type=ml_isolation_forest" \
  -H "Authorization: Bearer TOKEN"

# Filtrer par règle montant élevé
curl "http://localhost:8000/api/anomalies/?anomaly_type=rule_high_amount" \
  -H "Authorization: Bearer TOKEN"

# Filtrer par règle horaire
curl "http://localhost:8000/api/anomalies/?anomaly_type=rule_odd_hour" \
  -H "Authorization: Bearer TOKEN"
```

**Dans le frontend** : ouvrez **Anomalies** → le menu déroulant affiche maintenant 7 types (3 nouveaux + 4 anciens).

---

### Test 5 — Recommandations avec reason (API)

```bash
curl http://localhost:8000/api/recommendations/ \
  -H "Authorization: Bearer TOKEN"
```

**Réponse attendue :** chaque recommandation a maintenant un champ `reason` :
```json
[
  {
    "category": "Alimentation",
    "message": "Vos dépenses en Alimentation sont prévues en hausse...",
    "reason": "Prévision Random Forest : 4 200 MAD (+67 % vs moyenne 2 510 MAD/mois sur 12 mois).",
    "priority": "high"
  }
]
```

**Dans le frontend** : ouvrez **Recommandations** → chaque carte affiche le message principal + la justification en italique en dessous.

---

### Test 6 — Suite de tests automatiques

```bash
cd backend
python -m pytest tests/test_api/test_ml_insights.py -v
```

Résultat attendu : **12 tests passés**.

```
TestMLMetrics::test_ml_metrics_requires_auth       PASSED
TestMLMetrics::test_ml_metrics_returns_list        PASSED
TestMLMetrics::test_rf_metrics_stored_after_upload PASSED
TestMLMetrics::test_rf_metrics_have_required_keys  PASSED
TestMLMetrics::test_rf_r2_is_float                 PASSED
TestFeatureImportance::test_feature_importance_requires_auth   PASSED
TestFeatureImportance::test_feature_importance_returns_list    PASSED
TestFeatureImportance::test_feature_importance_has_6_features  PASSED
TestFeatureImportance::test_feature_importance_sum_is_1        PASSED
TestFeatureImportance::test_feature_importance_fields          PASSED
TestAnomalyNewTypes::test_anomaly_types_include_new_names      PASSED
TestRecommendationReason::test_recommendations_have_reason_field PASSED
```

---

## 17. Structure du projet

```
PE/
├── .env / .env.example
├── README.md
├── docker-compose.yml
│
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── docs/
│   └── AI_MODULE_EXPLANATION.md   ← explication technique complète du module IA
│
├── data/
│   ├── raw/    transactions_bancaires_synthetiques_brutes.csv
│   └── processed/
│       ├── transactions_nettoyees.csv
│       └── transactions_segmentees.csv   ← utilisé pour évaluer le classifieur LR
│
├── notebooks/
│   ├── 04_ml_categorization.ipynb
│   ├── 05_anomaly_detection.ipynb
│   └── 06_model_evaluation.ipynb
│
└── backend/
    ├── apps/
    │   ├── accounts/          Authentification JWT
    │   ├── transactions/      Upload CSV, liste des transactions
    │   ├── analytics/         KPIs, catégories, évolution, ml-metrics, feature-importance
    │   │   ├── models.py      MLModelMetrics (NEW)
    │   │   └── views.py       MLMetricsView, FeatureImportanceView (NEW)
    │   ├── anomalies/         Types : ml_isolation_forest, rule_high_amount, rule_odd_hour
    │   └── recommendations/   Recommendation.reason (NEW)
    │
    ├── pipeline/
    │   ├── ingestion/         load_csv(), validate_columns()
    │   ├── preprocessing/     clean(), normalize(), engineer_features()
    │   ├── categorization/    classify() — TF-IDF+LR ou règles
    │   ├── anomaly_detection/ detect() — IF + règles simultanés (mis à jour)
    │   ├── prediction/        train() — RF + sauvegarde métriques (mis à jour)
    │   └── recommendations/   generate() — signaux enrichis + reason (mis à jour)
    │
    ├── services/
    │   └── pipeline_service.py   Passe anomaly_summary à generate() (mis à jour)
    │
    ├── models_store/          .pkl des modèles entraînés
    │
    └── tests/
        ├── test_api/
        │   ├── test_ml_insights.py   ← 12 nouveaux tests (NEW)
        │   ├── test_analytics.py
        │   ├── test_anomalies.py
        │   ├── test_recommendations.py
        │   └── test_transactions.py, test_auth.py
        └── test_pipeline/
            ├── test_classifier.py
            └── test_cleaner.py
```
