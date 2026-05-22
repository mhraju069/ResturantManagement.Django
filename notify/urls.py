from django.urls import path
from .views import RegisterDeviceView, NotificationListView, MarkNotificationReadView, DashboardDataAPIView, FirebaseConfigAPIView

urlpatterns = [
    path('register-device/', RegisterDeviceView.as_view(), name='register_device'),
    path('list/', NotificationListView.as_view(), name='notification_list'),
    path('mark-read/', MarkNotificationReadView.as_view(), name='mark_all_read'),
    path('mark-read/<int:pk>/', MarkNotificationReadView.as_view(), name='mark_single_read'),
    path('dashboard-api/', DashboardDataAPIView.as_view(), name='dashboard_data_api'),
    path('firebase-config/', FirebaseConfigAPIView.as_view(), name='firebase_config'),
]
