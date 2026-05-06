from rest_framework import serializers
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
    
    class Meta:
        model = ProductCart
        fields = ('cart_items','final_amount')

    def get_final_amount(self, obj):
        return sum(item.quantity * item.food_item.price for item in obj.cart_items.all())



class CartUpdateSerializer(serializers.Serializer):
    food_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField()

    
    