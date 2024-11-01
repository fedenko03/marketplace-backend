from rest_framework import serializers

from backend import settings
from .models import Product, UserProductInteraction, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    liked = serializers.SerializerMethodField()
    viewed = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'image_url', 'created_at', 'liked', 'viewed']

    def get_liked(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return UserProductInteraction.objects.filter(
            user=user,
            product=obj,
            interaction_type=UserProductInteraction.LIKE
        ).exists()

    def get_viewed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return UserProductInteraction.objects.filter(
            user=user,
            product=obj,
            interaction_type=UserProductInteraction.VIEW
        ).exists()

    def get_image_url(self, obj):
        if obj.image:
            return f"{settings.BASE_URL}{obj.image.url}"
        return None


class UserProductInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductInteraction
        fields = ['id', 'user', 'product', 'interaction_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
