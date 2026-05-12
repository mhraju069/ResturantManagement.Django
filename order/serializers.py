from rest_framework import serializers
from .models import *


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('order',)


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        order_items = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item in order_items:
            OrderItem.objects.create(order=order, **item)
        return order

    
class ChargesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Charges
        exclude = ('id','active',)


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ('id', 'active',)
    