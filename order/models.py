import uuid
from django.db import models
from django.conf import settings
from product.models import FoodItem

# Create your models here.



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    first_name = models.CharField(max_length=200,verbose_name="First Name")
    last_name = models.CharField(max_length=200,verbose_name="Last Name")
    email = models.EmailField(verbose_name="User Email")
    phone = models.CharField(max_length=15, verbose_name="Phone Number")
    address = models.CharField(max_length=250, verbose_name="Address")
    city = models.CharField(max_length=50, verbose_name="City")
    state = models.CharField(max_length=50, verbose_name="State")
    zip_code = models.CharField(max_length=6, verbose_name="Zip Code")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Order {self.id} by {self.user}'



class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    