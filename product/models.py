from django.db import models
import uuid
from django.conf import settings
# Create your models here.


class FoodItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class FoodImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='food_images/')

    def __str__(self):
        return f"Image for {self.food.name}"



class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    foods = models.ManyToManyField(FoodItem,related_name='menu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Menu for {self.date}"




class ProductCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart for {self.user.email}"




class CartItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(ProductCart, on_delete=models.CASCADE,related_name='cart_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE,related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Cart item for {self.cart.user.email}"


