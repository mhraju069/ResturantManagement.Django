from django.contrib import admin
from .models import Payments
from unfold.admin import ModelAdmin

@admin.register(Payments)
class PaymentsAdmin(ModelAdmin):
    list_display = ('user', 'amount', 'status', 'tnxid', 'created_at', 'has_invoice')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'tnxid')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    @admin.display(boolean=True, description='Invoice')
    def has_invoice(self, obj):
        return bool(obj.invoice)