from django.urls import path

from .views import AnomalyListView, AnomalySummaryView

urlpatterns = [
    path('', AnomalyListView.as_view(), name='anomaly_list'),
    path('summary/', AnomalySummaryView.as_view(), name='anomaly_summary'),
]
