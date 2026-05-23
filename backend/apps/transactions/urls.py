from django.urls import path

from .views import TransactionListView, UploadBatchDeleteView, UploadBatchListView, UploadCSVView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload_csv'),
    path('', TransactionListView.as_view(), name='transaction_list'),
    path('batches/', UploadBatchListView.as_view(), name='batch_list'),
    path('batches/<int:batch_id>/delete/', UploadBatchDeleteView.as_view(), name='batch_delete'),
]
