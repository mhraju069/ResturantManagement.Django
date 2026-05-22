from rest_framework import serializers
from .models import FCMDevice, Notification

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['id', 'token', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        token = validated_data['token']
        # Avoid duplicate tokens for same/different users
        device, created = FCMDevice.objects.get_or_create(token=token, defaults={'user': user})
        if not created:
            device.user = user
            device.save()
        return device

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'order_id', 'created_at']
