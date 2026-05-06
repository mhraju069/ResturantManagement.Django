from django.urls import path
from .views import *



urlpatterns = [
    path('orders/', OrderApiView.as_view(), name='order'),
]