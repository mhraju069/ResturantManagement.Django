from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin


# Register your models here.

admin.site.register(FoodItem, ModelAdmin)
admin.site.register(ProductCart, ModelAdmin)
admin.site.register(CartItems, ModelAdmin)
