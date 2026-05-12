import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from product.models import FoodItem

# Create your models here.



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('preparing', 'Preparing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=50, verbose_name="Order ID", blank=True, null=True, unique=True)
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
        return f'Order {self.order_id} by {self.user}'
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            count = Order.objects.count() + 1
            self.order_id = f"ORD-{timezone.now().year}-{count:04d}"
        super().save(*args, **kwargs)



class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(choices=(('fixed', 'Fixed'), ('percent', 'Percent')), max_length=10)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_type} - {self.discount_value} - {self.active}"



class Charges(models.Model):
    CHARGE_TYPES = (
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage'),
    )

    name = models.CharField(max_length=100) 
    charge_type = models.CharField(choices=CHARGE_TYPES, max_length=10)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.charge_type} - {self.value} - {self.active}"



class ApplyCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apply_cupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.coupon.code} - {self.amount} - {self.applied_at}"


