from django.contrib import admin
from .models import FCMDevice, Notification
from unfold.admin import ModelAdmin
@admin.register(FCMDevice)
class FCMDeviceAdmin(ModelAdmin):
    list_display = ('user', 'token_truncated', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'token')

    def token_truncated(self, obj):
        return f"{obj.token[:40]}..." if obj.token else "-"
    token_truncated.short_description = 'Token'

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'order_id', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message', 'order_id')
    readonly_fields = ('created_at',)
