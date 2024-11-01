from datetime import datetime
from decimal import Decimal

from bson import Decimal128
from django.db import models, transaction, connection
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, F

from backend.responces import error_response
from user.order.models import CartItem, Order, OrderItem
from user.order.serializers import CartItemSerializer, OrderSerializer
from user.catalog.models import Product


class CartView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        product_id = data.get('product')
        quantity_to_set = int(data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return error_response("Товар не найден", status.HTTP_404_NOT_FOUND)

        if quantity_to_set > product.quantity:
            return error_response(f"Нельзя добавить больше {product.quantity} единиц этого товара.", status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity_to_set}
        )
        if not created:
            cart_item.quantity = quantity_to_set
            cart_item.save()

        return Response(self.get_serializer(cart_item).data, status=status.HTTP_201_CREATED)


class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({"message": "Товар удален из корзины"}, status=status.HTTP_200_OK)


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return error_response("Корзина пуста", status.HTTP_404_NOT_FOUND)

        insufficient_stock = []
        total_price = Decimal(0)

        for item in cart_items:
            if item.quantity > item.product.quantity:
                insufficient_stock.append({
                    "product": item.product.name,
                    "available_quantity": item.product.quantity
                })

            total_price += item.product.price * item.quantity

        if insufficient_stock:
            return error_response("Недостаточно товаров на складе", status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(user=user, total_price=total_price)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.quantity -= item.quantity
            item.product.save()

        cart_items.delete()

        return Response(
            {
                "message": "Менеджер свяжется с Вами по контактным данным (номеру телефона либо email)",
                "order_id": order.id,
                "total_price": str(total_price)
            },
            status=status.HTTP_201_CREATED
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
