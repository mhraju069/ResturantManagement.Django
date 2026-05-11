from rest_framework import serializers
from .models import FeedBack, ContactInfo, SupportMessage

class FeedBackSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()
    class Meta:
        model = FeedBack
        exclude = ('is_active',)

    def get_likes(self,obj):
        return obj.likes.count()

    def get_is_like(self,obj):
        request = self.context.get('request')
        return obj.likes.filter(id=request.user.id).exists()

class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        exclude = ('id','is_active','created_at',)

class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        exclude = ('id','created_at',)
