from django.urls import path, include
from .views import (
    ProductListView,
    ProductDetailView,
    UserInteractionView,
    LikedProductsView,
    ViewedProductsView, RecommendationView, CategoryListView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/interactions/', UserInteractionView.as_view(), name='product-interaction'),
    path('products/liked/', LikedProductsView.as_view(), name='liked-products'),
    path('products/viewed/', ViewedProductsView.as_view(), name='viewed-products'),

    path('recommendations/', RecommendationView.as_view(), name='product-recommendations'),
]