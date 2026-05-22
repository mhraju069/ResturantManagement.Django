from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import *

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'quantity')

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    actions = ['mark_as_accepted', 'mark_as_completed']

    def mark_as_accepted(self, request, queryset):
        for order in queryset:
            order.status = 'ACCEPTED'
            order.save()
    mark_as_accepted.short_description = "Mark selected orders as Accepted"

    def mark_as_completed(self, request, queryset):
        for order in queryset:
            order.status = 'COMPLETED'
            order.save()
    mark_as_completed.short_description = "Mark selected orders as Completed"

@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'active')
    list_filter = ('discount_type', 'active')

@admin.register(Charges)
class ChargesAdmin(ModelAdmin):
    list_display = ('name', 'charge_type', 'value', 'active')
    list_filter = ('charge_type', 'active')

admin.site.register(ApplyCoupon,ModelAdmin)
