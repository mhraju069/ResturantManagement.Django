from .views import *
from django.urls import path

urlpatterns = [
    path('food-items/', GetFoodItemApiView.as_view(), name='get_food_item'),
    path('cart-items/', GetcartItemsApiView.as_view(), name='get_cart_items'),
    path('cart-items/<str:action>/', UpdateCartApiView.as_view(), name='update_cart'),
]