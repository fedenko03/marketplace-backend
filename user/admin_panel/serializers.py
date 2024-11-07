from rest_framework import serializers

from backend import settings
from user.admin_panel.models import Log
from user.catalog.models import Category, Product
from user.models import User
from user.order.models import Order, OrderItem


class LogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Log
        fields = ['id', 'user', 'action', 'model_name', 'object_id', 'timestamp', 'details']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'role']
        read_only_fields = ['email']

    def validate(self, data):
        request = self.context.get('request')

        if 'role' in data and request:
            if request.user == self.instance:
                raise serializers.ValidationError("Вы не можете изменить свою роль.")

        return data

    def update(self, instance, validated_data):
        validated_data.pop('email', None)
        validated_data.pop('role', None)

        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    image = serializers.ImageField(required=False, write_only=True)
    image_url = serializers.SerializerMethodField()
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_id', 'price', 'quantity', 'created_at', 'image', 'image_url']
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        if obj.image:
            return f"{settings.BASE_URL}{obj.image.url}"
        return None


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_category = serializers.CharField(source='product.category.name', read_only=True)
    product_price = serializers.DecimalField(source='price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_description', 'product_category', 'quantity', 'product_price']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, default='created')
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'items', 'total_price', 'status']
        read_only_fields = ['user', 'created_at', 'items', 'total_price']
