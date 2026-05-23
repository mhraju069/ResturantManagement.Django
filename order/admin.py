from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import *

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_id', 'user_name_display', 'phone', 'food_items_display', 'total_amount', 'status', 'property', 'created_at','updated_at')
    list_filter = ('status', 'created_at','property','updated_at')
    search_fields = ('order_id', 'user__email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    list_display_links = ('order_id', 'user_name_display')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('order_id', 'user', ('property', 'status'), 'created_at', 'updated_at')
        }),
        ('Customer Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code')
        }),
        ('Payment', {
            'fields': ('total_amount',)
        }),
    )

    def user_name_display(self, obj):
        return f"{str(obj.first_name)} {str(obj.last_name)}"
    user_name_display.short_description = "User Name"

    def food_items_display(self, obj):
        return ", ".join([f"{item.quantity}x {item.food_item.name}" for item in obj.order_items.all()])
    food_items_display.short_description = "Food Items"
    
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
# admin.site.register(OrderItem,ModelAdmin)