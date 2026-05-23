from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.anomalies.models import Anomaly
from services.pipeline_service import PipelineError, PipelineService

from .models import Transaction, UploadBatch
from .serializers import TransactionSerializer, UploadBatchSerializer

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class UploadCSVView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.endswith('.csv'):
            return Response({'error': 'Only CSV files are accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        if file_obj.size > _MAX_FILE_SIZE:
            return Response(
                {'error': 'File exceeds the 10 MB limit.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = PipelineService.run(file_obj, request.user, file_obj.name)
            return Response(result, status=status.HTTP_201_CREATED)
        except PipelineError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class TransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).prefetch_related('anomalies')
        p = self.request.query_params
        if p.get('direction'):
            qs = qs.filter(direction=p['direction'])
        if p.get('category'):
            qs = qs.filter(category=p['category'])
        if p.get('search'):
            from django.db.models import Q
            q = p['search']
            qs = qs.filter(Q(narration__icontains=q) | Q(merchant_name__icontains=q) | Q(transaction_id__icontains=q))
        return qs


class UploadBatchListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadBatchSerializer

    def get_queryset(self):
        return UploadBatch.objects.filter(user=self.request.user)


class UploadBatchDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, batch_id):
        try:
            batch = UploadBatch.objects.get(id=batch_id, user=request.user)
        except UploadBatch.DoesNotExist:
            return Response({'error': 'Batch introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        txns = Transaction.objects.filter(batch=batch)
        txn_count = txns.count()
        anomaly_count = Anomaly.objects.filter(transaction__batch=batch).count()

        # Delete transactions (anomalies cascade via FK)
        txns.delete()
        batch.delete()

        return Response({
            'deleted_transactions': txn_count,
            'deleted_anomalies': anomaly_count,
            'message': 'Batch supprimé avec succès',
        }, status=status.HTTP_200_OK)
