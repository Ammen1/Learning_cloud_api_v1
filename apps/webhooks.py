import json
import hmac
import hashlib
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class WebhookHandler:
    """
    Base class for handling webhooks.
    """
    
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or getattr(settings, 'WEBHOOK_SECRET_KEY', '')
    
    def verify_signature(self, payload, signature):
        """
        Verify webhook signature using HMAC-SHA256.
        """
        if not self.secret_key:
            return True  # Skip verification if no secret key is set
        
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, event_type, data):
        """
        Process webhook data based on event type.
        Override this method in subclasses.
        """
        raise NotImplementedError


class PaymentWebhookHandler(WebhookHandler):
    """
    Handles payment-related webhooks.
    """
    
    def process_webhook(self, event_type, data):
        """
        Process payment webhook events.
        """
        if event_type == 'payment.completed':
            return self.handle_payment_completed(data)
        elif event_type == 'payment.failed':
            return self.handle_payment_failed(data)
        elif event_type == 'subscription.created':
            return self.handle_subscription_created(data)
        elif event_type == 'subscription.cancelled':
            return self.handle_subscription_cancelled(data)
        else:
            logger.warning(f"Unknown payment webhook event: {event_type}")
            return {"status": "ignored", "message": "Unknown event type"}
    
    def handle_payment_completed(self, data):
        """
        Handle payment completed event.
        """
        try:
            # Update user's premium status
            from apps.accounts.models import User
            user_id = data.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.is_premium = True
                user.premium_expires_at = timezone.now() + timezone.timedelta(days=30)
                user.save()
                
                # Send notification
                from apps.notifications.views import send_notification
                send_notification(
                    user,
                    "Payment Successful",
                    "Your premium subscription has been activated!",
                    notification_type='PAYMENT_SUCCESS',
                    priority='HIGH'
                )
                
                logger.info(f"Payment completed for user {user.username}")
                return {"status": "success", "message": "Payment processed"}
        except Exception as e:
            logger.error(f"Error processing payment completion: {e}")
            return {"status": "error", "message": str(e)}
    
    def handle_payment_failed(self, data):
        """
        Handle payment failed event.
        """
        try:
            from apps.accounts.models import User
            user_id = data.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                
                # Send notification
                from apps.notifications.views import send_notification
                send_notification(
                    user,
                    "Payment Failed",
                    "Your payment could not be processed. Please try again.",
                    notification_type='PAYMENT_FAILED',
                    priority='HIGH'
                )
                
                logger.info(f"Payment failed for user {user.username}")
                return {"status": "success", "message": "Payment failure processed"}
        except Exception as e:
            logger.error(f"Error processing payment failure: {e}")
            return {"status": "error", "message": str(e)}
    
    def handle_subscription_created(self, data):
        """
        Handle subscription created event.
        """
        try:
            from apps.accounts.models import User
            user_id = data.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.is_premium = True
                user.premium_expires_at = timezone.now() + timezone.timedelta(days=30)
                user.save()
                
                logger.info(f"Subscription created for user {user.username}")
                return {"status": "success", "message": "Subscription processed"}
        except Exception as e:
            logger.error(f"Error processing subscription creation: {e}")
            return {"status": "error", "message": str(e)}
    
    def handle_subscription_cancelled(self, data):
        """
        Handle subscription cancelled event.
        """
        try:
            from apps.accounts.models import User
            user_id = data.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.is_premium = False
                user.premium_expires_at = None
                user.save()
                
                # Send notification
                from apps.notifications.views import send_notification
                send_notification(
                    user,
                    "Subscription Cancelled",
                    "Your premium subscription has been cancelled.",
                    notification_type='SUBSCRIPTION_CANCELLED',
                    priority='MEDIUM'
                )
                
                logger.info(f"Subscription cancelled for user {user.username}")
                return {"status": "success", "message": "Subscription cancellation processed"}
        except Exception as e:
            logger.error(f"Error processing subscription cancellation: {e}")
            return {"status": "error", "message": str(e)}


class ContentWebhookHandler(WebhookHandler):
    """
    Handles content-related webhooks.
    """
    
    def process_webhook(self, event_type, data):
        """
        Process content webhook events.
        """
        if event_type == 'content.updated':
            return self.handle_content_updated(data)
        elif event_type == 'content.published':
            return self.handle_content_published(data)
        elif event_type == 'content.deleted':
            return self.handle_content_deleted(data)
        else:
            logger.warning(f"Unknown content webhook event: {event_type}")
            return {"status": "ignored", "message": "Unknown event type"}
    
    def handle_content_updated(self, data):
        """
        Handle content updated event.
        """
        try:
            from apps.content.models import Lesson
            lesson_id = data.get('lesson_id')
            if lesson_id:
                lesson = Lesson.objects.get(id=lesson_id)
                lesson.updated_at = timezone.now()
                lesson.save()
                
                logger.info(f"Content updated for lesson {lesson.title}")
                return {"status": "success", "message": "Content update processed"}
        except Exception as e:
            logger.error(f"Error processing content update: {e}")
            return {"status": "error", "message": str(e)}
    
    def handle_content_published(self, data):
        """
        Handle content published event.
        """
        try:
            from apps.content.models import Lesson
            lesson_id = data.get('lesson_id')
            if lesson_id:
                lesson = Lesson.objects.get(id=lesson_id)
                lesson.is_active = True
                lesson.published_at = timezone.now()
                lesson.save()
                
                logger.info(f"Content published for lesson {lesson.title}")
                return {"status": "success", "message": "Content publication processed"}
        except Exception as e:
            logger.error(f"Error processing content publication: {e}")
            return {"status": "error", "message": str(e)}
    
    def handle_content_deleted(self, data):
        """
        Handle content deleted event.
        """
        try:
            from apps.content.models import Lesson
            lesson_id = data.get('lesson_id')
            if lesson_id:
                lesson = Lesson.objects.get(id=lesson_id)
                lesson.is_active = False
                lesson.save()
                
                logger.info(f"Content deleted for lesson {lesson.title}")
                return {"status": "success", "message": "Content deletion processed"}
        except Exception as e:
            logger.error(f"Error processing content deletion: {e}")
            return {"status": "error", "message": str(e)}


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """
    Generic webhook view that can handle different types of webhooks.
    """
    
    def post(self, request, webhook_type):
        """
        Handle webhook POST requests.
        """
        try:
            # Get webhook data
            payload = request.body
            signature = request.META.get('HTTP_X_SIGNATURE', '')
            
            # Parse JSON data
            try:
                data = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            
            # Get event type
            event_type = data.get('event_type')
            if not event_type:
                return JsonResponse({"error": "Missing event_type"}, status=400)
            
            # Get appropriate handler
            handler = self.get_handler(webhook_type)
            if not handler:
                return JsonResponse({"error": "Unknown webhook type"}, status=400)
            
            # Verify signature
            if not handler.verify_signature(payload, signature):
                return JsonResponse({"error": "Invalid signature"}, status=401)
            
            # Process webhook
            result = handler.process_webhook(event_type, data)
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)
    
    def get_handler(self, webhook_type):
        """
        Get the appropriate webhook handler based on type.
        """
        handlers = {
            'payment': PaymentWebhookHandler(),
            'content': ContentWebhookHandler(),
        }
        return handlers.get(webhook_type)


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request):
    """
    Handle payment webhooks.
    """
    view = WebhookView()
    return view.post(request, 'payment')


@csrf_exempt
@require_http_methods(["POST"])
def content_webhook(request):
    """
    Handle content webhooks.
    """
    view = WebhookView()
    return view.post(request, 'content')


@csrf_exempt
@require_http_methods(["POST"])
def generic_webhook(request, webhook_type):
    """
    Handle generic webhooks.
    """
    view = WebhookView()
    return view.post(request, webhook_type)


# Webhook registration functionality
class WebhookRegistration:
    """
    Handles webhook registration and management.
    """
    
    def __init__(self):
        self.registered_webhooks = {}
    
    def register_webhook(self, url, events, secret=None):
        """
        Register a new webhook.
        """
        webhook_id = f"webhook_{len(self.registered_webhooks) + 1}"
        self.registered_webhooks[webhook_id] = {
            'url': url,
            'events': events,
            'secret': secret,
            'created_at': timezone.now(),
            'is_active': True
        }
        return webhook_id
    
    def unregister_webhook(self, webhook_id):
        """
        Unregister a webhook.
        """
        if webhook_id in self.registered_webhooks:
            del self.registered_webhooks[webhook_id]
            return True
        return False
    
    def get_webhook(self, webhook_id):
        """
        Get webhook details.
        """
        return self.registered_webhooks.get(webhook_id)
    
    def list_webhooks(self):
        """
        List all registered webhooks.
        """
        return self.registered_webhooks


# Global webhook registration instance
webhook_registry = WebhookRegistration()


@csrf_exempt
@require_http_methods(["POST"])
def register_webhook(request):
    """
    Register a new webhook.
    """
    try:
        data = json.loads(request.body)
        url = data.get('url')
        events = data.get('events', [])
        secret = data.get('secret')
        
        if not url:
            return JsonResponse({"error": "URL is required"}, status=400)
        
        if not events:
            return JsonResponse({"error": "Events list is required"}, status=400)
        
        webhook_id = webhook_registry.register_webhook(url, events, secret)
        
        return JsonResponse({
            "message": "Webhook registered successfully",
            "webhook_id": webhook_id,
            "url": url,
            "events": events
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Webhook registration error: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_webhooks(request):
    """
    List all registered webhooks.
    """
    try:
        webhooks = webhook_registry.list_webhooks()
        return JsonResponse({"webhooks": webhooks})
        
    except Exception as e:
        logger.error(f"Webhook listing error: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def unregister_webhook(request, webhook_id):
    """
    Unregister a webhook.
    """
    try:
        if webhook_registry.unregister_webhook(webhook_id):
            return JsonResponse({"message": "Webhook unregistered successfully"})
        else:
            return JsonResponse({"error": "Webhook not found"}, status=404)
            
    except Exception as e:
        logger.error(f"Webhook unregistration error: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)