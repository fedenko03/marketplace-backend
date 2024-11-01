from django.contrib import admin

from user.catalog.models import Product, Category, UserProductInteraction


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'created_at')
    search_fields = ('work_name', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')


@admin.register(UserProductInteraction)
class UserProductInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'interaction_type', 'created_at')


