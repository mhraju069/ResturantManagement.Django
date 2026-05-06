from rest_framework import generics,status
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *



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
            "message": "Food items fetched successfully",
            "data": serializer.data
        })




class GetcartItemsApiView(generics.ListAPIView):
    serializer_class = ProductCartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset, _ = ProductCart.objects.get_or_create(user=self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        
        return Response({
            "success": True,
            "message": "Cart items fetched successfully",
            "data": serializer.data
        })




class UpdateCartApiView(generics.GenericAPIView):
    serializer_class = CartUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request,action):
        serializer = self.get_serializer(data=request.data)

        if action not in ['add', 'remove']:
            return Response({
                "success": False,
                "message": "Invalid action",
            }, status=status.HTTP_400_BAD_REQUEST)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        food_item_id = serializer.validated_data['food_item_id']
        quantity = serializer.validated_data['quantity']

        try:
            food_item = FoodItem.objects.filter(id=food_item_id).first()

            if not food_item:
                return Response({
                    "success": False,
                    "message": "Food item not found",
                }, status=status.HTTP_404_NOT_FOUND)
                
            cart,_ = ProductCart.objects.get_or_create(user=self.request.user)
            item, created = CartItems.objects.get_or_create(cart=cart,food_item=food_item,defaults={'quantity':quantity})

            if action == 'add':
                if not created:
                    item.quantity+= quantity

            elif action == 'remove':
                item.quantity-= quantity
                if item.quantity <= 0:
                    item.delete()

                    return Response({
                        "success": True,
                        "message": "Cart item deleted successfully",
                    })
            
            item.save()
                    
            return Response({
                "success": True,
                "message": "Cart items added successfully",
            })

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)