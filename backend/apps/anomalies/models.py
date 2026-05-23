from django.db import models


class Anomaly(models.Model):
    TYPE_HIGH_AMOUNT = 'high_amount'
    TYPE_ODD_HOUR = 'odd_hour'
    TYPE_CATEGORY_SPIKE = 'category_spike'
    TYPE_UNUSUAL_FREQUENCY = 'unusual_frequency'
    # New unified type names (used when both IF + rules run simultaneously)
    TYPE_ML_ISOLATION_FOREST = 'ml_isolation_forest'
    TYPE_RULE_HIGH_AMOUNT = 'rule_high_amount'
    TYPE_RULE_ODD_HOUR = 'rule_odd_hour'

    TYPE_CHOICES = [
        (TYPE_HIGH_AMOUNT, 'Unusually High Amount'),
        (TYPE_ODD_HOUR, 'Transaction at Unusual Hour'),
        (TYPE_CATEGORY_SPIKE, 'Category Spending Spike'),
        (TYPE_UNUSUAL_FREQUENCY, 'Unusual Transaction Frequency'),
        (TYPE_ML_ISOLATION_FOREST, 'Unusual Spending Pattern (Isolation Forest)'),
        (TYPE_RULE_HIGH_AMOUNT, 'Rule: Unusually High Amount'),
        (TYPE_RULE_ODD_HOUR, 'Rule: Transaction at Unusual Hour'),
    ]

    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.CASCADE,
        related_name='anomalies',
    )
    anomaly_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    score = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'anomalies'
        ordering = ['-score']

    def __str__(self):
        return f"{self.anomaly_type} — {self.transaction.transaction_id} (score={self.score:.2f})"
