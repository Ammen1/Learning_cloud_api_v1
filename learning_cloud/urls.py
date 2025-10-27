"""
URL configuration for Learning Cloud project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('health/', lambda request: JsonResponse({"status": "ok"})),
    path('admin/', admin.site.urls),
    path('api/auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.content.urls')),
    path('api/', include('apps.quizzes.urls')),
    path('api/', include('apps.progress.urls')),
    path('api/', include('apps.analytics.urls')),
    path('api/', include('apps.notifications.urls')),
    path('webhooks/', include('apps.webhook_urls')),
    # API Documentation - each endpoint loads schema separately to avoid 431 error
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI (loads schema via AJAX to avoid large headers)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc (handles large schemas better)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Internationalization URLs
urlpatterns += i18n_patterns(
    path('', include('apps.accounts.urls')),
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


