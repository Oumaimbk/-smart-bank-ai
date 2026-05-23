from django.db.models import Count
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Anomaly
from .serializers import AnomalySerializer


class AnomalyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnomalySerializer

    def get_queryset(self):
        qs = (
            Anomaly.objects
            .filter(transaction__user=self.request.user)
            .select_related('transaction')
        )
        anomaly_type = self.request.query_params.get('anomaly_type')
        if anomaly_type:
            qs = qs.filter(anomaly_type=anomaly_type)
        return qs


class AnomalySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Anomaly.objects.filter(transaction__user=request.user)
        total = qs.count()
        by_type = dict(qs.values_list('anomaly_type').annotate(n=Count('id')).values_list('anomaly_type', 'n'))
        return Response({
            'total': total,
            'by_type': by_type,
        })
