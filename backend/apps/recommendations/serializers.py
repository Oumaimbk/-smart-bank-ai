from rest_framework import serializers

from .models import Prediction, Recommendation


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'category', 'target_period', 'predicted_amount', 'created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'category', 'message', 'reason', 'priority', 'created_at']
