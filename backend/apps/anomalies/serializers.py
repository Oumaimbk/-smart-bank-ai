from rest_framework import serializers

from .models import Anomaly


class AnomalySerializer(serializers.ModelSerializer):
    transaction_id = serializers.CharField(source='transaction.transaction_id', read_only=True)
    transaction_date = serializers.DateField(source='transaction.transaction_date', read_only=True)
    amount = serializers.DecimalField(
        source='transaction.amount', max_digits=12, decimal_places=2, read_only=True
    )
    category = serializers.CharField(source='transaction.category', read_only=True)
    merchant_name = serializers.CharField(source='transaction.merchant_name', read_only=True)

    class Meta:
        model = Anomaly
        fields = [
            'id', 'transaction_id', 'transaction_date', 'amount',
            'category', 'merchant_name', 'anomaly_type', 'score',
            'description', 'created_at',
        ]
