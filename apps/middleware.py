from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from apps.accounts.models import UserSession
import logging
import time

logger = logging.getLogger(__name__)

class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting for API endpoints.
    """
    
    def process_request(self, request):
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
            
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Rate limiting rules
        rate_limits = {
            '/api/auth/login/': {'requests': 5, 'window': 60},  # 5 requests per minute
            '/api/auth/register/': {'requests': 3, 'window': 60},  # 3 requests per minute
            '/api/quizzes/': {'requests': 20, 'window': 60},  # 20 requests per minute
            '/api/progress/': {'requests': 30, 'window': 60},  # 30 requests per minute
            '/api/analytics/': {'requests': 10, 'window': 60},  # 10 requests per minute
        }
        
        # Check rate limits
        for path, limits in rate_limits.items():
            if request.path.startswith(path):
                if self.is_rate_limited(client_ip, path, limits):
                    logger.warning(f"Rate limit exceeded for IP {client_ip} on path {request.path}")
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests. Limit: {limits["requests"]} requests per {limits["window"]} seconds',
                        'retry_after': limits['window']
                    }, status=429)
                break
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_ip, path, limits):
        """Check if the client has exceeded the rate limit."""
        cache_key = f"rate_limit:{client_ip}:{path}"
        current_time = timezone.now().timestamp()
        
        # Get existing requests from cache
        requests = cache.get(cache_key, [])
        
        # Remove old requests outside the time window
        window_start = current_time - limits['window']
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(requests) >= limits['requests']:
            return True
        
        # Add current request
        requests.append(current_time)
        cache.set(cache_key, requests, limits['window'])
        
        return False


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and responses for analytics.
    """
    
    def process_request(self, request):
        # Skip logging for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
            
        # Store request start time
        request.start_time = time.time()
        
        # Log request
        logger.info(f"API Request: {request.method} {request.path} - IP: {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        # Skip logging for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return response
            
        # Calculate response time
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            logger.info(f"API Response: {request.method} {request.path} - Status: {response.status_code} - Time: {response_time:.3f}s")
            
            # Log slow requests
            if response_time > 2.0:  # More than 2 seconds
                logger.warning(f"Slow API request: {request.method} {request.path} - Time: {response_time:.3f}s")
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity and update last seen.
    """
    
    def process_request(self, request):
        # Skip for non-API requests
        if not request.path.startswith('/api/'):
            return None
            
        # Update user's last seen if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Update last seen timestamp
                request.user.last_login = timezone.now()
                request.user.save(update_fields=['last_login'])
                
                # Track session activity
                if hasattr(request, 'session'):
                    session_key = request.session.session_key
                    if session_key:
                        UserSession.objects.filter(
                            user=request.user,
                            session_key=session_key
                        ).update(last_activity=timezone.now())
                        
            except Exception as e:
                logger.error(f"Error updating user activity: {e}")
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add CORS headers for API requests
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Origin'] = '*'  # Configure this properly in production
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        return response
