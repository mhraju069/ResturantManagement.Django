from rest_framework import serializers
from .models import *

class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(source='plan.price',read_only=True)
    
    class Meta:
        model = Payments
        fields = '__all__'

class CheckoutSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        plan_id = attrs.get('plan_id')
        
        try:         
            plan = Plan.objects.get(id=plan_id)
            return plan
        except Plan.DoesNotExist:
            raise serializers.ValidationError({"status":False,"log":"Plan not found"})


class PaymentIntentSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(max_length=255, required=True)
    coupon = serializers.CharField(max_length=20, required=False)
    first_name = serializers.CharField(max_length=200,required=True)
    last_name = serializers.CharField(max_length=200,required=True)
    address = serializers.CharField(max_length=250, required=True)
    city = serializers.CharField(max_length=50, required=True)
    state = serializers.CharField(max_length=50, required=True)
    zip_code = serializers.CharField(max_length=6, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    email = serializers.EmailField(required=True)