from rest_framework import generics,permissions
from .models import Order
from .serializers import OrderSerializer

class OrderApiView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    