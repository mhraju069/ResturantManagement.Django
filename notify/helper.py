import logging
import firebase_admin
from firebase_admin import messaging
from .models import FCMDevice, Notification
from authentication.models import User

logger = logging.getLogger(__name__)

def send_fcm_notification(user, title, message, data=None):
    """
    Sends a push notification to a user's registered FCM devices.
    Also creates a Notification object in the DB.
    """
    # 1. Create Notification object in database
    order_id = None
    if data and 'order_id' in data:
        order_id = data['order_id']
    Notification.objects.create(user=user, title=title, message=message, order_id=order_id)

    # 2. Get registered FCM devices for this user
    devices = FCMDevice.objects.filter(user=user)
    tokens = [d.token for d in devices if d.token]

    if not tokens:
        logger.info(f"No FCM devices registered for user {user.email}")
        return

    # Prepare message data (must be strings)
    msg_data = {}
    if data:
        for k, v in data.items():
            msg_data[k] = str(v)

    # FCM allows sending to multiple tokens using MulticastMessage
    message_payload = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(
            title=title,
            body=message,
        ),
        data=msg_data,
        webpush=messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                title=title,
                body=message,
                icon='/static/speed_icon.png', # Placeholder or dashboard symbol icon
            )
        )
    )

    try:
        # Check if firebase app is initialized
        if not firebase_admin._apps:
            logger.warning("Firebase Admin is not initialized. Skipping push notification sending.")
            return

        response = messaging.send_multicast(message_payload)
        logger.info(f"Successfully sent {response.success_count} notifications; failed {response.failure_count}")
        # Clean up invalid/expired tokens
        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    # If token is invalid/expired, delete it
                    invalid_token = tokens[idx]
                    FCMDevice.objects.filter(token=invalid_token).delete()
                    logger.info(f"Deleted invalid FCM token: {invalid_token[:20]}...")
    except Exception as e:
        logger.error(f"Error sending FCM notification: {e}")

def notify_admins_new_order(order):
    """
    Notifies all admins when a new order is placed.
    """
    admins = User.objects.filter(role='admin', is_active=True)
    title = "New Order Placed"
    message = f"Order {order.order_id} has been placed by {order.first_name} {order.last_name} for ${order.total_amount}."
    data = {
        "order_id": str(order.id),
        "type": "new_order"
    }
    for admin in admins:
        send_fcm_notification(admin, title, message, data)

def notify_user_order_status(order):
    """
    Notifies the user about their order status changes.
    """
    status_label = dict(order.STATUS_CHOICES).get(order.status, order.status)
    title = f"Order Status Update: {status_label}"
    message = f"Your order {order.order_id} is now {status_label}."
    data = {
        "order_id": str(order.id),
        "status": order.status,
        "type": "order_status_change"
    }
    send_fcm_notification(order.user, title, message, data)
