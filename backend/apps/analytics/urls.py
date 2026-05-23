from django.urls import path

from .views import (
    DashboardKPIView,
    FeatureImportanceView,
    MLMetricsView,
    MonthlyEvolutionView,
    SpendingByCategoryView,
    TopMerchantsView,
)

urlpatterns = [
    path('kpi/', DashboardKPIView.as_view(), name='kpi'),
    path('spending-by-category/', SpendingByCategoryView.as_view(), name='spending_by_category'),
    path('monthly-evolution/', MonthlyEvolutionView.as_view(), name='monthly_evolution'),
    path('top-merchants/', TopMerchantsView.as_view(), name='top_merchants'),
    path('ml-metrics/', MLMetricsView.as_view(), name='ml_metrics'),
    path('feature-importance/', FeatureImportanceView.as_view(), name='feature_importance'),
]
