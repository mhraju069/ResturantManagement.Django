from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FCMDevice, Notification
from .serializers import FCMDeviceSerializer, NotificationSerializer

class RegisterDeviceView(generics.CreateAPIView):
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)[:20]

class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        if pk:
            try:
                notification = Notification.objects.get(pk=pk, user=request.user)
                notification.is_read = True
                notification.save()
                return Response({"status": True, "message": "Notification marked as read"})
            except Notification.DoesNotExist:
                return Response({"status": False, "message": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return Response({"status": True, "message": "All notifications marked as read"})

from django.shortcuts import render
from django.conf import settings

def firebase_messaging_sw(request):
    config = {
        "apiKey": settings.FIREBASE_API_KEY,
        "authDomain": settings.FIREBASE_AUTH_DOMAIN,
        "projectId": settings.FIREBASE_PROJECT_ID,
        "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
        "messagingSenderId": settings.FIREBASE_MESSAGING_SENDER_ID,
        "appId": settings.FIREBASE_APP_ID,
        "measurementId": settings.FIREBASE_MEASUREMENT_ID,
        "vapidKey": settings.FIREBASE_VAPID_KEY,
    }
    return render(request, "firebase-messaging-sw.js", {"firebase_config": config}, content_type="application/javascript")


from config.admin import get_dashboard_live_data

class DashboardDataAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            data = get_dashboard_live_data()
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FirebaseConfigAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "apiKey": getattr(settings, "FIREBASE_API_KEY", ""),
            "authDomain": getattr(settings, "FIREBASE_AUTH_DOMAIN", ""),
            "projectId": getattr(settings, "FIREBASE_PROJECT_ID", ""),
            "storageBucket": getattr(settings, "FIREBASE_STORAGE_BUCKET", ""),
            "messagingSenderId": getattr(settings, "FIREBASE_MESSAGING_SENDER_ID", ""),
            "appId": getattr(settings, "FIREBASE_APP_ID", ""),
            "measurementId": getattr(settings, "FIREBASE_MEASUREMENT_ID", ""),
            "vapidKey": getattr(settings, "FIREBASE_VAPID_KEY", ""),
        })
