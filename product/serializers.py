from rest_framework import serializers
from payment.helper import final_price
from .models import *


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        exclude = ('is_active','created_at', 'updated_at')



class CartItemsSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItems
        exclude = ('cart','id')

    def get_total_price(self, obj):
        return obj.quantity * obj.food_item.price



class ProductCartSerializer(serializers.ModelSerializer):
    cart_items = CartItemsSerializer(many=True, read_only=True)
    final_amount = serializers.SerializerMethodField()
    coupon = serializers.CharField(max_length=20, required=False)
    
    class Meta:
        model = ProductCart
        fields = ('cart_items','final_amount','coupon')

    def get_final_amount(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
            
        subtotal = sum(item.quantity * item.food_item.price for item in obj.cart_items.all())        
        
        # Get coupon from query params or request data
        coupon = request.query_params.get('coupon') or request.data.get('coupon')
        
        return final_price(request, subtotal, coupon)



class CartUpdateSerializer(serializers.Serializer):
    food_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField()

    
    