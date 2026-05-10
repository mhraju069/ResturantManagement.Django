from django.urls import path
from .views import *

urlpatterns = [
    path('place-order/', PlaceOrderView.as_view(), name='create_checkout_session'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
    path('payment-demo/', PaymentDemoView.as_view(), name='payment_demo'),
]
