from django.contrib import admin
from .models import User
from unfold.admin import ModelAdmin
from django import forms
from core.widgets import PremiumImageUpload


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'image': PremiumImageUpload(),
        }

@admin.register(User)
class UserAdmin(ModelAdmin):
    form = UserAdminForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "image", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "block", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    readonly_fields = ('created_at', 'last_login')