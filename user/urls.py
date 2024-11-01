from django.urls import path, include

from user.views import UserProfileView

urlpatterns = [
    path('auth/', include('user.authentication.urls')),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('catalog/', include('user.catalog.urls')),
    path('cart/', include('user.order.urls')),
    path('admin/', include('user.admin_panel.urls')),
]
