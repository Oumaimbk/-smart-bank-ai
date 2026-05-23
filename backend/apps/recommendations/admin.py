from django.contrib import admin

from .models import Prediction, Recommendation


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'target_period', 'predicted_amount', 'created_at')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'priority', 'category', 'created_at')
    list_filter = ('priority',)
