from django.urls import path
from .views import CartView, RemoveFromCartView, OrderCreateView, OrderListView, OrderDetailView

urlpatterns = [
    path('', CartView.as_view(), name='cart-view'),
    path('remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('order/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
