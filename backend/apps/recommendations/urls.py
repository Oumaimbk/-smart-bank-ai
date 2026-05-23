from django.urls import path

from .views import PredictionListView, RecommendationListView

urlpatterns = [
    path('predictions/', PredictionListView.as_view(), name='prediction_list'),
    path('', RecommendationListView.as_view(), name='recommendation_list'),
]
