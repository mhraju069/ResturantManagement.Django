from django.urls import path
from .views import *

urlpatterns = [
    path('feedback/', FeedBackListCreate.as_view(), name='feedback-list-create'),
    path('feedback/like/<uuid:feedback_id>/', AddLikeToFeedback.as_view(), name='add-like-to-feedback'),
    path('contact-info/', ContactInfoListCreate.as_view(), name='contact-info-list-create'),
    path('support-messages/', SupportMessageListCreate.as_view(), name='support-message-list-create'),
]
