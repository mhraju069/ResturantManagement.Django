from django.contrib import admin
from django.urls import path, include
from . import swagger
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from config.admin import admin_activity_log
from notify.views import firebase_messaging_sw

urlpatterns = [
    path('firebase-messaging-sw.js', firebase_messaging_sw, name='firebase_messaging_sw'),
    path('admin/activity-log/', admin_activity_log, name='admin_activity_log'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("auth/api/v1/", include("authentication.urls")),
    path("subscription/api/v1/", include("subscription.urls")),
    path("payment/api/v1/", include("payment.urls")),
    path("product/api/v1/", include("product.urls")),
    path("order/api/v1/", include("order.urls")),
    path("other/api/v1/", include("other.urls")),
    path("notify/api/v1/", include("notify.urls")),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("docs/", swagger.schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", swagger.schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

]
