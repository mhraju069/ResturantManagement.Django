from django.core.management.base import BaseCommand
from authentication.models import User
from notify.helper import send_fcm_notification
from order.models import Order

class Command(BaseCommand):
    help = 'Sends demo notifications to admins and users for testing Firebase notifications.'

    def add_arguments(self, parser):
        parser.add_argument('--user-email', type=str, help='Email of the user to notify')
        parser.add_argument('--admin-email', type=str, help='Email of the admin to notify')

    def handle(self, *args, **options):
        # Fetch first order from database for realistic redirection links
        first_order = Order.objects.first()
        order_id = str(first_order.id) if first_order else "demo-uuid-123"
        order_label = first_order.order_id if (first_order and first_order.order_id) else "V-9988"
        # 1. Notify Admin
        admin_email = options.get('admin_email')
        if admin_email:
            admins = User.objects.filter(email=admin_email, role='admin')
        else:
            admins = User.objects.filter(role='admin', is_active=True)

        if admins.exists():
            for admin in admins:
                self.stdout.write(self.style.SUCCESS(f"Sending demo admin notification to {admin.email}..."))
                send_fcm_notification(
                    user=admin,
                    title="Demo: New Order Received!",
                    message=f"Order #{order_label} has been successfully placed by a customer for $120.50.",
                    data={"order_id": order_id, "type": "new_order"}
                )
            self.stdout.write(self.style.SUCCESS("Admin notification dispatched. Check the admin dashboard dropdown!"))
        else:
            # Fallback: if no admin role user exists, check any staff or active user
            admins = User.objects.filter(is_staff=True, is_active=True)
            if admins.exists():
                for admin in admins:
                    self.stdout.write(self.style.SUCCESS(f"Sending demo admin notification to staff user {admin.email}..."))
                    send_fcm_notification(
                        user=admin,
                        title="Demo: New Order Received!",
                        message=f"Order #{order_label} has been successfully placed by a customer for $120.50.",
                        data={"order_id": order_id, "type": "new_order"}
                    )
            else:
                self.stdout.write(self.style.WARNING("No active admin/staff user found to send admin demo notifications."))

        # 2. Notify User
        user_email = options.get('user_email')
        if user_email:
            users = User.objects.filter(email=user_email)
        else:
            users = User.objects.filter(role='user', is_active=True)

        if not users.exists():
            users = User.objects.filter(is_active=True).exclude(pk=admins.first().pk if admins.exists() else None)

        if users.exists():
            user = users.first()
            self.stdout.write(self.style.SUCCESS(f"Sending demo user notification to {user.email}..."))
            send_fcm_notification(
                user=user,
                title="Order Status: Preparing 🍳",
                message=f"Your order #{order_label} is now being prepared. Get ready!",
                data={"order_id": order_id, "status": "PREPARING", "type": "order_status_change"}
            )
            self.stdout.write(self.style.SUCCESS("User notification dispatched."))
        else:
            self.stdout.write(self.style.WARNING("No active user found to send user demo notifications."))
