from rest_framework import generics,permissions
from .models import Order
from .serializers import OrderSerializer

class OrderApiView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    