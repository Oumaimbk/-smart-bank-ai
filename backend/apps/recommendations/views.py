from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Prediction, Recommendation
from .serializers import PredictionSerializer, RecommendationSerializer


class PredictionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PredictionSerializer
    pagination_class = None  # return all predictions at once (small dataset)

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user)


class RecommendationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationSerializer
    pagination_class = None

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)
