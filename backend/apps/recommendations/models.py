from django.conf import settings
from django.db import models


class Prediction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    category = models.CharField(max_length=50)
    target_period = models.CharField(max_length=7)  # "YYYY-MM"
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'predictions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category', 'target_period'],
                name='unique_user_category_period',
            )
        ]
        ordering = ['category']

    def __str__(self):
        return f"{self.user} | {self.category} | {self.target_period} → {self.predicted_amount}"


class Recommendation(models.Model):
    PRIORITY_HIGH = 'high'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_LOW = 'low'

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_LOW, 'Low'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations',
    )
    category = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    reason = models.TextField(blank=True, default='')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"[{self.priority.upper()}] {self.category}: {self.message[:60]}"
