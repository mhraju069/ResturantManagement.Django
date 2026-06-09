from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import *

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    change_list_template = 'admin/order/order/change_list.html'
    
    list_display = ('order_id', 'user_name_display', 'phone', 'food_items_display', 'total_amount', 'status', 'property', 'created_at','updated_at')
    list_filter = ('status', 'created_at','property','updated_at')
    search_fields = ('order_id', 'user__email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    list_display_links = ('order_id', 'user_name_display')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('api/list/', self.admin_site.admin_view(self.api_list_orders), name='order-admin-api-list'),
            path('api/update/', self.admin_site.admin_view(self.api_update_order), name='order-admin-api-update'),
        ]
        return custom_urls + urls

    def api_list_orders(self, request):
        from django.http import JsonResponse
        from payment.models import Payments
        orders = Order.objects.prefetch_related('order_items__food_item').all().order_by('-created_at')
        data = []
        for o in orders:
            items = []
            for item in o.order_items.all():
                items.append({
                    'name': item.food_item.name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total': float(item.price * item.quantity),
                })
            
            # Retrieve payment transaction ID if present
            pmt = o.payments_set.exclude(tnxid__isnull=True).exclude(tnxid='').first()
            stripe_refund_link = f"https://dashboard.stripe.com/payments/{pmt.tnxid}" if pmt and pmt.tnxid else None
            
            data.append({
                'id': str(o.id),
                'order_id': o.order_id or '',
                'first_name': o.first_name,
                'last_name': o.last_name,
                'phone': o.phone,
                'status': o.status,
                'prep_time': o.prep_time,
                'total_amount': float(o.total_amount),
                'created_at_time': o.created_at.strftime('%I:%M %p') if o.created_at else '',
                'created_at': o.created_at.isoformat() if o.created_at else '',
                'items': items,
                'stripe_refund_link': stripe_refund_link,
            })
        return JsonResponse({'orders': data})

    def api_update_order(self, request):
        import json
        from django.http import JsonResponse
        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        try:
            payload = json.loads(request.body)
            order_id = payload.get('order_id')
            status = payload.get('status')
            prep_time = payload.get('prep_time')
            
            order = Order.objects.get(id=order_id)
            if status:
                order.status = status
            if prep_time is not None:
                order.prep_time = prep_time
            order.save()
            return JsonResponse({
                'status': 'success', 
                'order_status': order.status, 
                'prep_time': order.prep_time
            })
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
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