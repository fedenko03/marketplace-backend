from decimal import Decimal

from bson import Decimal128
from django.db import models

from user.models import User


class Decimal128Field(models.DecimalField):
    """
    Custom field to handle MongoDB Decimal128 compatibility.
    """

    def from_db_value(self, value, expression, connection):
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value

    def get_prep_value(self, value):
        if isinstance(value, Decimal):
            return Decimal128(value)
        elif isinstance(value, str):
            return Decimal128(Decimal(value))
        return value


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="products", blank=True, null=True)
    price = Decimal128Field(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class UserProductInteraction(models.Model):
    VIEW = 'view'
    LIKE = 'like'

    INTERACTION_TYPES = [
        (VIEW, 'View'),
        (LIKE, 'Like'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.interaction_type})"


