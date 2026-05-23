from django.contrib import admin

from .models import Transaction, UploadBatch


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ('user', 'filename', 'status', 'transaction_count', 'created_at')
    list_filter = ('status',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'direction', 'amount', 'category', 'transaction_date')
    list_filter = ('direction', 'category')
    search_fields = ('transaction_id', 'narration', 'merchant_name')
