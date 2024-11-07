from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from backend.responces import field_errors_response, error_response
from user.admin_panel.models import Log
from user.admin_panel.permissions import IsSuperAdminOrManager
from user.admin_panel.serializers import ProductSerializer, CategorySerializer, UserSerializer, OrderSerializer, \
    LogSerializer
from user.catalog.models import Category, Product
from user.catalog.pagination import CustomPagination
from user.models import User
from user.order.models import Order


def log_action(user, action, model_name, object_id=None, details=None):
    Log.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        details=details
    )


class AdminLogListView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'model_name']

    def get_queryset(self):
        queryset = Log.objects.all().order_by('-timestamp')
        user = self.request.query_params.get('user')
        action = self.request.query_params.get('action')
        model_name = self.request.query_params.get('model_name')

        if user:
            queryset = queryset.filter(user=user)
        if action:
            queryset = queryset.filter(action=action)
        if model_name:
            queryset = queryset.filter(model_name=model_name)

        return queryset

    def format_log(self, log):
        details = ", ".join(f"{key}: {value}" for key, value in log.details.items()) if log.details else "No details"
        return f"ID: {log.id} | User: {log.user} | Action: {log.action} | Model: {log.model_name} | Object ID: {log.object_id or 'N/A'} | Time: {log.timestamp} | Details: {details}"

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        formatted_logs = [self.format_log(log) for log in queryset]
        return Response(formatted_logs, status=status.HTTP_200_OK)


class AdminUserListView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)


class AdminUserDetailView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return error_response("Пользователь не найден", status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user, context=self.get_serializer_context())
        return Response(serializer.data)

    def patch(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return error_response("Пользователь не найден", status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user, data=request.data, partial=True, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'update', 'User', pk, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return field_errors_response(serializer)

    def delete(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return error_response("Пользователь не найден", status.HTTP_404_NOT_FOUND)
        user.delete()
        log_action(request.user, 'delete', 'User', pk)
        return Response({"message": "Пользователь удален"}, status=status.HTTP_200_OK)


class AdminCategoryListView(generics.GenericAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def get(self, request):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'post', 'Category', None, request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return field_errors_response(serializer)


class AdminCategoryDetailView(generics.GenericAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def get(self, request, pk):
        category = Category.objects.filter(pk=pk).first()
        if not category:
            return error_response("Категория не найдена", status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(category)
        return Response(serializer.data)

    def patch(self, request, pk):
        category = Category.objects.filter(pk=pk).first()
        if not category:
            return error_response("Категория не найдена", status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'update', 'Category', pk, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return field_errors_response(serializer)

    def delete(self, request, pk):
        category = Category.objects.filter(pk=pk).first()
        if not category:
            return error_response("Категория не найдена", status.HTTP_404_NOT_FOUND)
        category.delete()
        log_action(request.user, 'delete', 'Category', pk)
        return Response({"message": "Категория удалена"}, status=status.HTTP_200_OK)


class AdminProductListView(generics.GenericAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def get(self, request):
        products = Product.objects.all()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        image = request.FILES.get('image')
        if image:
            data['image'] = image

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'post', 'Product', None, request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return field_errors_response(serializer)


class AdminProductDetailView(generics.GenericAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def get(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return error_response("Товар не найден", status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(product)
        return Response(serializer.data)

    def patch(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return error_response("Товар не найден", status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        image = request.FILES.get('image')
        if image:
            if product.image:
                product.image.delete()
            data['image'] = image

        serializer = self.serializer_class(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'update', 'Product', pk, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return field_errors_response(serializer)

    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return error_response("Товар не найден", status.HTTP_404_NOT_FOUND)
        product.delete()
        log_action(request.user, 'delete', 'Product', pk)
        return Response({"message": "Товар удален"}, status=status.HTTP_200_OK)


class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]


class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrManager]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == 'canceled':
            return error_response("Статус заказа уже отменен и не может быть изменен.")

        new_status = request.data.get('status')

        if new_status == 'canceled':
            for item in instance.items.all():
                item.product.quantity += item.quantity
                item.product.save()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(request.user, 'update', 'Order', instance.id, request.data)
        return Response({"message": "Статус заказа обновлен", "order": serializer.data}, status=status.HTTP_200_OK)