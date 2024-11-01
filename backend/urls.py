from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from backend import settings

urlpatterns = [
    path('api/admin-django/', admin.site.urls),
    path('api/', include('user.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)