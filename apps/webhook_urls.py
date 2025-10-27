from django.urls import path
from . import webhooks

urlpatterns = [
    path('payment/', webhooks.payment_webhook, name='payment_webhook'),
    path('content/', webhooks.content_webhook, name='content_webhook'),
    path('<str:webhook_type>/', webhooks.generic_webhook, name='generic_webhook'),
    
    # Webhook registration
    path('register/', webhooks.register_webhook, name='register_webhook'),
    path('list/', webhooks.list_webhooks, name='list_webhooks'),
    path('unregister/<str:webhook_id>/', webhooks.unregister_webhook, name='unregister_webhook'),
]
