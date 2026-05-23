from typing import Optional

import pandas as pd


def generate(
    df: pd.DataFrame,
    predictions: list,
    anomaly_summary: Optional[dict] = None,
) -> list:
    """
    Rule-based recommendation engine.

    Combines three signals:
      1. Budget trend — predicted vs historical monthly average per category.
      2. Anomaly alerts — categories with unusual spending patterns detected.
      3. Top spenders — categories with consistently high absolute spending.

    Each recommendation includes a 'reason' field explaining the data behind it.
    """
    debits = df[df['direction'] == 'Debit'].copy()
    if debits.empty:
        return []

    debits['transaction_date'] = pd.to_datetime(debits['transaction_date'])
    debits['period'] = debits['transaction_date'].dt.to_period('M')

    monthly_avg: dict[str, float] = (
        debits.groupby(['period', 'category'])['amount']
        .sum()
        .groupby('category')
        .mean()
        .to_dict()
    )

    pred_map = {p['category']: float(p['predicted_amount']) for p in predictions}
    anomaly_by_cat: dict[str, int] = (anomaly_summary or {}).get('by_category', {})

    recommendations: list[dict] = []

    for category, avg in monthly_avg.items():
        predicted = pred_map.get(category, avg)
        change_pct = ((predicted - avg) / avg * 100) if avg > 0 else 0
        n_months = debits[debits['category'] == category]['period'].nunique()

        if change_pct > 50:
            recommendations.append({
                'category': category,
                'message': (
                    f"Vos dépenses en {category} sont prévues en hausse de {change_pct:.0f} % "
                    f"le mois prochain ({predicted:.0f} MAD vs moyenne {avg:.0f} MAD). "
                    f"Envisagez de définir un budget strict pour cette catégorie."
                ),
                'reason': (
                    f"Prévision Random Forest : {predicted:.0f} MAD "
                    f"(+{change_pct:.0f} % par rapport à la moyenne historique de {avg:.0f} MAD/mois "
                    f"sur {n_months} mois analysés)."
                ),
                'priority': 'high',
            })
        elif change_pct > 20:
            recommendations.append({
                'category': category,
                'message': (
                    f"Les dépenses en {category} pourraient augmenter de {change_pct:.0f} % "
                    f"le mois prochain ({predicted:.0f} MAD vs moyenne {avg:.0f} MAD). Restez vigilant."
                ),
                'reason': (
                    f"Prévision Random Forest : {predicted:.0f} MAD "
                    f"(+{change_pct:.0f} % vs moyenne {avg:.0f} MAD/mois sur {n_months} mois)."
                ),
                'priority': 'medium',
            })
        elif avg > 1500:
            recommendations.append({
                'category': category,
                'message': (
                    f"Vous dépensez en moyenne {avg:.0f} MAD/mois en {category}. "
                    f"Revoir cette catégorie pourrait réduire vos dépenses mensuelles."
                ),
                'reason': (
                    f"Catégorie à fort volume : moyenne {avg:.0f} MAD/mois "
                    f"sur {n_months} mois analysés."
                ),
                'priority': 'low',
            })

    for category, n_anomalies in anomaly_by_cat.items():
        if n_anomalies >= 1:
            recommendations.append({
                'category': category,
                'message': (
                    f"{n_anomalies} transaction{'s' if n_anomalies > 1 else ''} inhabituelle"
                    f"{'s' if n_anomalies > 1 else ''} détectée{'s' if n_anomalies > 1 else ''} "
                    f"en {category}. Vérifiez ces opérations dans l'onglet Anomalies."
                ),
                'reason': (
                    f"Détection combinée Isolation Forest + règles statistiques. "
                    f"{n_anomalies} signal{'s' if n_anomalies > 1 else ''} pour cette catégorie."
                ),
                'priority': 'high' if n_anomalies >= 3 else 'medium',
            })

    return sorted(
        recommendations,
        key=lambda r: {'high': 0, 'medium': 1, 'low': 2}[r['priority']],
    )
