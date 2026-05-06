from django.shortcuts import render
from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer
# Create your views here.


class OrderApiView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    