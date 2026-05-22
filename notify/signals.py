from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from order.models import Order
from .helper import (
    notify_admins_new_order, 
    notify_user_order_status, 
    send_payment_complete_email, 
    send_order_ready_email
)

@receiver(pre_save, sender=Order)
def cache_old_status(sender, instance, **kwargs):
    if instance.id:
        try:
            instance._old_status = Order.objects.get(pk=instance.id).status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    # Case 1: Order is first marked as NEW (this means it went from pending -> NEW upon payment success)
    if new_status == 'NEW' and (old_status == 'pending' or old_status is None):
        notify_admins_new_order(instance)
        send_payment_complete_email(instance)

    # Case 2: Order status changes from admin panel or API
    elif old_status is not None and old_status != new_status:
        if new_status in ['ACCEPTED', 'PREPARING', 'READY', 'PICKED_UP', 'COMPLETED']:
            notify_user_order_status(instance)
        if new_status == 'READY':
            send_order_ready_email(instance)
