# helper.py
import stripe
from django.conf import settings
from django.urls import reverse
stripe.api_key = settings.STRIPE_SECRET_KEY
from order.serializers import OrderSerializer


def create_checkout_session(request, payment , price ):

    if price is None or payment is None:
        raise Exception("Required data for Checkout Session is missing")
    
    session_data = {
        "payment_method_types": ["card"],
        "mode": "payment",
        "line_items": [
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(price * 100),
                    "product_data": {
                        "name": "Confirm your subscription",
                    },
                },
                "quantity": 1 ,
            }
        ],
        "success_url": request.build_absolute_uri(reverse("payment_success")),
        "cancel_url": request.build_absolute_uri(reverse("payment_cancel")),
        "invoice_creation": {
            "enabled": True,
        },
        "metadata": {
            "payment": str(payment.id)
        },
        "payment_intent_data": {
            "metadata": {
                "payment": str(payment.id)
            }
        },
        "invoice_creation": {
            "enabled": True,
            "invoice_data": {
                "metadata": {
                    "payment": str(payment.id)
                }
            }
        }
    }

    session = stripe.checkout.Session.create(**session_data)

    return session.url


from .models import Payments
from product.models import ProductCart, CartItems

def Place_order(data, request):
    user = request.user
    try:
        cart = ProductCart.objects.get(user=user)
        cart_items = cart.cart_items.all()
    except ProductCart.DoesNotExist:
        return {"status": False, "message": "Cart not found"}

    if not cart_items.exists():
        return {"status": False, "message": "Cart is empty"}

    total_amount = 0
    order_items_data = []
    for item in cart_items:
        total_amount += item.food_item.price * item.quantity
        order_items_data.append({
            'food_item': item.food_item.id,
            'quantity': item.quantity,
            'price': item.food_item.price
        })

    data['total_amount'] = float(total_amount)
    data['user'] = user.id
    data['order_items'] = order_items_data

    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        order = serializer.save()
        # Clear cart
        # cart_items.delete()
        return {"status": True, "order": order}
    else:
        return {"status": False, "errors": serializer.errors}




def Create_payment_intent(data, request, order):
    payment_method_id = data['payment_method_id']

    try:
        # Create a pending payment record
        payment = Payments.objects.create(
            user=request.user,
            order=order,
            amount=order.total_amount,
            status='pending'
        )

        # Create and confirm the payment intent using the provided payment_method_id
        intent = stripe.PaymentIntent.create(
            amount=int(float(order.total_amount) * 100),
            currency='usd',
            payment_method=payment_method_id,
            confirm=True,
            off_session=True,
            metadata={
                "payment": payment.id,
                "order": str(order.id),
                "user": request.user.email
            },
            return_url=request.build_absolute_uri('/payment/success/')
        )

        if intent.status == 'succeeded':
            # Update order status
            order.status = 'paid'
            order.save()
            
            return {
                "status": True,
                "payment_id": payment.id,
                "client_secret": intent.client_secret
            }
        elif intent.status == 'requires_action' or intent.status == 'requires_source_action':
            return {
                "status": True,
                "client_secret": intent.client_secret,
                "requires_action": True
            }
        else:
            return {
                "status": False,
            }

    except stripe.error.CardError as e:
        return {
            "status": False,
            "message": f"Card Error: {e.user_message if hasattr(e, 'user_message') else str(e)}",
        }
    except Exception as e:
        return {
            "status": False,
            "message": f"Error: {str(e)}", 
        }