from django.contrib import admin

from .models import Anomaly


@admin.register(Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'anomaly_type', 'score', 'created_at')
    list_filter = ('anomaly_type',)
