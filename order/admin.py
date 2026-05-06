from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import *


admin.site.register(Order, ModelAdmin)
admin.site.register(OrderItem, ModelAdmin)