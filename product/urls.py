from .views import *
from django.urls import path

urlpatterns = [
    path('food-items/', GetFoodItemApiView.as_view(), name='get_food_item'),
]