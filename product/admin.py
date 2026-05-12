from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin, TabularInline
from django import forms
from core.widgets import PremiumImageUpload


# Register your models here.


class FoodImageInlineForm(forms.ModelForm):
    class Meta:
        model = FoodImage
        fields = '__all__'
        widgets = {
            'image': PremiumImageUpload(),
        }


class FoodImageInline(TabularInline):
    model = FoodImage
    form = FoodImageInlineForm
    extra = 1

@admin.register(FoodItem)
class FoodItemAdmin(ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    search_fields = ('name', 'category')
    list_filter = ('category', 'is_active')
    inlines = [FoodImageInline]
    compressed_fields = True
    
    fieldsets = (
        ("General Information", {
            "fields": ("name", "category", "price", "is_active"),
        }),
        ("Details", {
            "fields": ('short_details','description',),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductCart)
class ProductCartAdmin(ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name')


@admin.register(CartItems)
class CartItemsAdmin(ModelAdmin):
    list_display = ('cart', 'food_item', 'quantity')


@admin.register(Menu)
class MenuAdmin(ModelAdmin):
    list_display = ('date', 'created_at')
    list_filter = ('date',)
    show_full_result_count = True
    search_fields = ('date', 'foods__name')
    autocomplete_fields = ('foods',)
    ordering = ('-date',)


