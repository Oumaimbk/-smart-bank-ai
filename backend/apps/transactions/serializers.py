from rest_framework import serializers

from .models import Transaction, UploadBatch


class UploadBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadBatch
        fields = [
            'id', 'filename', 'status', 'transaction_count',
            'error_message', 'created_at', 'processed_at',
        ]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    is_anomalous = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'transaction_date', 'transaction_time',
            'account_type', 'payment_method', 'direction', 'amount',
            'balance_after', 'narration', 'merchant_name', 'merchant_city',
            'merchant_country', 'category', 'is_anomalous', 'created_at',
        ]

    def get_is_anomalous(self, obj):
        return obj.anomalies.exists()
