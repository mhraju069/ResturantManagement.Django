from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin, TabularInline


# Register your models here.


class FoodImageInline(TabularInline):
    model = FoodImage
    extra = 1

@admin.register(FoodItem)
class FoodItemAdmin(ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    search_fields = ('name', 'category')
    list_filter = ('category', 'is_active')
    inlines = [FoodImageInline]


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


