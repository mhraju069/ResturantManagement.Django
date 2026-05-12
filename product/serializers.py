from rest_framework import serializers
from payment.helper import final_price
from .models import *
from order.serializers import ChargesSerializer, CouponSerializer
from order.models import Charges, Coupon


class FoodImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodImage
        fields = ('image',)



class FoodItemSerializer(serializers.ModelSerializer):
    images = FoodImageSerializer(many=True, read_only=True)
    class Meta:
        model = FoodItem
        fields = ('id', 'name', 'category', 'short_details', 'description', 'price', 'images')



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
    coupon = serializers.SerializerMethodField()
    charges = serializers.SerializerMethodField()

    
    class Meta:
        model = ProductCart
        fields = ('cart_items','final_amount','coupon','charges')

    
    def get_charges(self, obj):
        charges = Charges.objects.filter(active=True)
        return ChargesSerializer(charges, many=True).data
        
    def get_coupon(self, obj):
        request = self.context.get('request')
        if not request:
            return None
            
        coupon_code = request.query_params.get('coupon') or request.data.get('coupon')
        if not coupon_code:
            return None
            
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code, active=True)
            return CouponSerializer(coupon_obj).data
        except Coupon.DoesNotExist:
            return None
        

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

    


class GetMenuSerializer(serializers.ModelSerializer):
    foods = FoodItemSerializer(many=True, read_only=True)
    class Meta:
        model = Menu
        fields = ('id','date','foods')