from django.conf import settings
from django.db import models


class UploadBatch(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='batches',
    )
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    transaction_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'upload_batches'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.filename} ({self.status})"


class Transaction(models.Model):
    DIRECTION_CREDIT = 'Credit'
    DIRECTION_DEBIT = 'Debit'
    DIRECTION_CHOICES = [
        (DIRECTION_CREDIT, 'Credit'),
        (DIRECTION_DEBIT, 'Debit'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    batch = models.ForeignKey(
        UploadBatch,
        on_delete=models.CASCADE,
        related_name='transactions',
    )

    transaction_id = models.CharField(max_length=50)
    customer_id = models.CharField(max_length=50, blank=True)
    transaction_date = models.DateField()
    transaction_time = models.TimeField(null=True, blank=True)
    account_type = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    narration = models.TextField(blank=True)
    merchant_name = models.CharField(max_length=100, blank=True)
    merchant_city = models.CharField(max_length=100, blank=True)
    merchant_country = models.CharField(max_length=10, blank=True)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date', '-transaction_time']
        constraints = [
            models.UniqueConstraint(fields=['user', 'transaction_id'], name='unique_user_transaction')
        ]

    def __str__(self):
        return f"{self.transaction_id} — {self.direction} {self.amount}"
