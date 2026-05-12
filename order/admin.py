from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem, Coupon, Charges

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'quantity')

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__email', 'first_name', 'last_name')
    inlines = [OrderItemInline]
    
    actions = ['mark_as_paid', 'mark_as_delivered']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = "Mark selected orders as Paid"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'active')
    list_filter = ('discount_type', 'active')

@admin.register(Charges)
class ChargesAdmin(ModelAdmin):
    list_display = ('name', 'charge_type', 'value', 'active')
    list_filter = ('charge_type', 'active')