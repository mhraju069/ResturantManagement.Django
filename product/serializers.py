from rest_framework import serializers
from .models import *


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        exclude = ('created_at', 'updated_at')