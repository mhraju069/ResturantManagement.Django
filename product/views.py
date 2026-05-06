from rest_framework import generics
from .serializers import *
from rest_framework.response import Response


class GetFoodItemApiView(generics.ListAPIView):
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        queryset = FoodItem.objects.filter(is_active=True)
        if self.request.query_params.get('category'):
            queryset = queryset.filter(category=self.request.query_params.get('category'))
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully",
            "data": serializer.data
        })