from django.contrib import admin
from .models import FeedBack, ContactInfo, SupportMessage
from unfold.admin import ModelAdmin

@admin.register(FeedBack)
class FeedBackAdmin(ModelAdmin):
    list_display = ('name', 'email', 'rating', 'is_active', 'created_at')
    list_filter = ('is_active', 'rating')
    search_fields = ('name', 'email', 'review')

@admin.register(ContactInfo)
class ContactInfoAdmin(ModelAdmin):
    list_display = ('email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('email', 'location', 'phone')

@admin.register(SupportMessage)
class SupportMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
