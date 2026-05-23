# Module IA — Explication technique

## 1. Vue d'ensemble du pipeline

À chaque import de fichier CSV, le pipeline exécute les étapes suivantes dans l'ordre :

```
CSV
 │
 ▼  Ingestion + validation des colonnes
 │
 ▼  Nettoyage (doublons, dates, montants, direction)
 │
 ▼  Normalisation + feature engineering
 │     → text_to_segment, hour, is_weekend, narration_normalized
 │
 ▼  [Modèle 1] TF-IDF + Régression Logistique
 │     → category, category_confidence
 │
 ▼  [Modèle 2] Isolation Forest + Règles statistiques (simultanément)
 │     → anomaly_type, score, description
 │
 ▼  [Modèle 3] Random Forest Regressor (ré-entraîné)
 │     → rf_expense_predictor.pkl, MAE, RMSE, R²
 │
 ▼  Prédictions mois suivant par catégorie
 │
 ▼  Recommandations (règles sur prévisions + anomalies)
```

---

## 2. Modèle 1 — TF-IDF + Régression Logistique (catégorisation)

### Pourquoi ce modèle ?
La catégorisation de transactions bancaires est un problème de **classification de texte court**.
TF-IDF est léger, interprétable, et très efficace sur des textes courts et structurés comme
les libellés bancaires. La Régression Logistique est transparente : les coefficients par classe
sont directement lisibles.

### Pipeline de vectorisation
```
text_to_segment = clean_merchant_name + ' ' + clean_narration (minuscules)
    │
    ▼
TfidfVectorizer(ngram_range=(1,2), max_features=10 000)
    │
    ▼
LogisticRegression(C=5, max_iter=1000, multi_class='multinomial')
    │
    ▼
category + category_confidence
```

### 11 catégories prises en charge
Alimentation · E-commerce · Factures · Logement · Loisirs · Retrait cash ·
Revenu · Santé · Shopping · Transport · Voyage

### Métriques d'évaluation (holdout 20 %)
| Métrique | Valeur |
|---|---|
| Accuracy | 100.00 % |
| F1 (weighted) | 1.0000 |
| F1 (macro) | 1.0000 |
| Précision | 1.0000 |
| Rappel | 1.0000 |

> Ces performances élevées s'expliquent par la nature **synthétique et structurée** du dataset :
> les libellés sont suffisamment distincts entre catégories pour qu'un modèle linéaire les sépare
> parfaitement. Sur des données réelles (libellés ambigus, abréviations, erreurs de saisie),
> des performances de 85–95 % seraient attendues.

### Fallback
Si les fichiers `.pkl` sont absents, un classifieur par règles (mots-clés) prend le relais.

---

## 3. Modèle 2 — Isolation Forest (détection de schémas inhabituels)

### Pourquoi Isolation Forest ?
La détection d'anomalies dans les transactions est un problème **non supervisé** : on ne dispose
pas d'étiquettes "frauduleux / normal". Isolation Forest est particulièrement adapté car :

- Il n'a pas besoin de supposer une distribution gaussienne des données.
- Il isole les anomalies par des coupures aléatoires successives : une transaction anormale
  est isolée plus rapidement (moins de coupures nécessaires).
- Il est rapide à l'inférence et robuste aux données de haute dimensionnalité.

### Features utilisées (4)
| Feature | Description |
|---|---|
| `amount` | Montant de la transaction (MAD) |
| `hour` | Heure de la transaction (0–23) |
| `is_weekend` | 1 si week-end, 0 sinon |
| `category_enc` | Catégorie encodée numériquement |

### Paramètres
```python
IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
```
`contamination=0.05` signifie que le modèle suppose que 5 % des transactions sont anormales.

### Méthode complémentaire — règles statistiques
En plus de l'Isolation Forest, deux règles s'appliquent systématiquement :

- **rule_high_amount** : z-score > 2.5 par rapport à la moyenne de la catégorie.
  Exemple : un achat de 9 000 MAD dans une catégorie où la moyenne est 100 MAD.
- **rule_odd_hour** : transaction entre 00h00 et 05h59.

Ces deux méthodes tournent **simultanément** sur chaque upload. Une transaction peut donc
être flaggée par l'Isolation Forest ET par une règle (types distincts dans la DB).

### Types d'anomalies stockés
| Type | Source |
|---|---|
| `ml_isolation_forest` | Isolation Forest |
| `rule_high_amount` | Règle z-score |
| `rule_odd_hour` | Règle horaire |

---

## 4. Modèle 3 — Random Forest Regressor (prévision mensuelle)

### Pourquoi Random Forest ?
La prévision des dépenses mensuelles est un problème de **régression sur données agrégées**.
Random Forest est choisi pour :

- Sa robustesse aux outliers (plusieurs arbres votent ensemble).
- Sa capacité à capturer des relations non linéaires entre features (saisonnalité, habitudes de week-end).
- Sa fourniture native des **importances de variables**, utile pour l'explicabilité.
- Sa bonne performance sans hyperparamétrage intensif.

### Agrégation des données
Les transactions Debit sont agrégées par `(mois, catégorie)`.
Une ligne d'entraînement = un mois × une catégorie.

### Features (6)
| Feature | Description | Importance typique |
|---|---|---|
| `avg_amount` | Montant moyen par transaction | ~40–50 % |
| `transaction_count` | Nombre de transactions ce mois | ~20–30 % |
| `period_int` | Numéro de période (trend temporel) | ~10–15 % |
| `month` | Numéro du mois (saisonnalité) | ~5–10 % |
| `category_enc` | Catégorie encodée | ~5–10 % |
| `is_weekend_ratio` | Proportion de transactions week-end | ~2–5 % |

### Hyperparamètres
```python
RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)
```

### Évaluation
À chaque upload CSV, le modèle est **ré-entraîné** sur toutes les données de l'utilisateur
avec un holdout 80/20 :

| Métrique | Définition |
|---|---|
| **MAE** (Mean Absolute Error) | Erreur absolue moyenne en MAD |
| **RMSE** (Root Mean Squared Error) | Pénalise les grandes erreurs |
| **R²** (coefficient de détermination) | 1.0 = parfait, 0.0 = modèle nul |

---

## 5. Recommandations

Le moteur de recommandations est **basé sur des règles** (pas de ML) pour garantir
la transparence et l'explicabilité :

| Signal | Condition | Priorité |
|---|---|---|
| Hausse prévue RF | > +50 % vs moyenne historique | haute |
| Hausse prévue RF | > +20 % vs moyenne historique | moyenne |
| Gros poste de dépense | Moyenne > 1 500 MAD/mois | basse |
| Anomalies par catégorie | ≥ 3 flags | haute |
| Anomalies par catégorie | 1–2 flags | moyenne |

Chaque recommandation inclut un champ `reason` qui cite les chiffres précis ayant
déclenché le conseil.

---

## 6. Limitations

1. **Dataset synthétique** : les libellés sont construits artificiellement avec des mots-clés
   distincts par catégorie. Sur des données réelles, l'accuracy du classifieur sera inférieure.

2. **Absence de séries temporelles** : le Random Forest ne modélise pas explicitement les
   dépendances temporelles. Un modèle ARIMA ou Prophet pourrait améliorer la saisonnalité.

3. **Contamination fixe** : le taux de 5 % pour l'Isolation Forest est un hyperparamètre choisi
   a priori. Sur les données d'un utilisateur réel, ce taux devrait être ajusté.

4. **Pas de réentraînement du classifieur** : TF-IDF + LR est entraîné une fois sur le dataset
   global (notebook). Il n'est pas personnalisé par utilisateur.

5. **Pas de vrai holdout temporel** : idéalement, l'évaluation RF se ferait sur les derniers mois
   (holdout temporel), pas sur un split aléatoire.

---

## 7. Améliorations futures

- [ ] Classifieur personnalisé par utilisateur (few-shot learning sur les corrections manuelles).
- [ ] Prophet ou LSTM pour la prévision de séries temporelles.
- [ ] Calibration du taux de contamination par analyse de la distribution des scores.
- [ ] Explainability avec SHAP pour les prédictions du Random Forest.
- [ ] Interface de correction des catégories pour générer des données étiquetées réelles.
- [ ] Alertes temps réel (webhooks) quand une anomalie critique est détectée.
