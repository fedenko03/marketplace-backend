from django.urls import path
from .views import (
    AdminUserListView, AdminUserDetailView,
    AdminCategoryListView, AdminCategoryDetailView,
    AdminProductListView, AdminProductDetailView,
    AdminOrderListView, AdminOrderDetailView
)

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin-users-list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),

    path('categories/', AdminCategoryListView.as_view(), name='admin-categories-list'),
    path('categories/<int:pk>/', AdminCategoryDetailView.as_view(), name='admin-category-detail'),

    path('products/', AdminProductListView.as_view(), name='admin-products-list'),
    path('products/<int:pk>/', AdminProductDetailView.as_view(), name='admin-product-detail'),

    path('orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
]