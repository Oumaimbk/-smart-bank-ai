from django.db import models


class MLModelMetrics(models.Model):
    model_name = models.CharField(max_length=50, unique=True)
    metrics = models.JSONField(default=dict)
    feature_importance = models.JSONField(default=list)
    sample_count = models.IntegerField(default=0)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ml_model_metrics'

    def __str__(self):
        return f"{self.model_name} — {self.computed_at:%Y-%m-%d %H:%M}"
