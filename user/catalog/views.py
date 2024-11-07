import random
from collections import Counter

from django.db.models import Max, Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from .models import Product, UserProductInteraction, Category
from .serializers import ProductSerializer, UserProductInteractionSerializer, CategorySerializer
from .filters import ProductFilter
from .pagination import CustomPagination


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []


class ProductListView(APIView):
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['id', 'price', 'created_at']
    ordering = ['-created_at']
    search_fields = ['name', 'description']

    def get(self, request):
        queryset = Product.objects.all()
        filtered_queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(filtered_queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserInteractionView(generics.CreateAPIView):
    serializer_class = UserProductInteractionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        interaction_type = request.data.get('interaction_type')
        product_id = request.data.get('product')

        if interaction_type == UserProductInteraction.LIKE:
            existing_like = UserProductInteraction.objects.filter(
                user=request.user,
                product_id=product_id,
                interaction_type=UserProductInteraction.LIKE
            ).first()

            if existing_like:
                existing_like.delete()
                return Response({"message": "Лайк удален"}, status=status.HTTP_200_OK)

        interaction = UserProductInteraction(
            user=request.user,
            product_id=product_id,
            interaction_type=interaction_type
        )
        interaction.save()

        if interaction_type == UserProductInteraction.LIKE:
            msg = 'Лайк поставлен'
        elif interaction_type == UserProductInteraction.VIEW:
            msg = 'Запись просмотрена'
        else:
            msg = 'Действие выполнено'

        return Response(
            {"message": msg},
            status=status.HTTP_201_CREATED
        )


class LikedProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        liked_products = UserProductInteraction.objects.filter(
            user=self.request.user, interaction_type=UserProductInteraction.LIKE
        ).values_list('product', flat=True)
        return Product.objects.filter(id__in=liked_products)


class ViewedProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        last_viewed_interactions = (
            UserProductInteraction.objects.filter(
                user=user,
                interaction_type=UserProductInteraction.VIEW
            )
            .values('product')
            .annotate(last_viewed=Max('created_at'))
            .order_by('-created_at')
        )
        product_ids = [interaction['product'] for interaction in last_viewed_interactions]

        return Product.objects.filter(id__in=product_ids).order_by('-created_at')


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        interactions = UserProductInteraction.objects.filter(user=user).order_by('-created_at')
        category_weight = Counter()
        for index, interaction in enumerate(interactions):
            try:
                category_id = interaction.product.category_id
            except Product.DoesNotExist:
                continue

            if interaction.interaction_type in [UserProductInteraction.LIKE, UserProductInteraction.VIEW]:
                weight = max(1, len(interactions) - index)
                category_weight[category_id] += weight

        sorted_categories = [cat_id for cat_id, _ in category_weight.most_common()]

        viewed_product_ids = set(UserProductInteraction.objects.filter(
            user=user,
            interaction_type=UserProductInteraction.VIEW
        ).values_list('product_id', flat=True).distinct())

        recommended_products = []
        for category_id in sorted_categories:
            try:
                products_in_category = Product.objects.filter(category_id=category_id).exclude(
                    id__in=viewed_product_ids)
            except Product.DoesNotExist:
                continue

            popular_products = (UserProductInteraction.objects
                                .filter(product__in=products_in_category)
                                .exclude(user=user)
                                .values('product')
                                .annotate(interaction_count=Count('product'))
                                .order_by('-interaction_count')[:5])

            popular_product_ids = [item['product'] for item in popular_products]
            recommended_products.extend(Product.objects.filter(id__in=popular_product_ids))

            if len(recommended_products) >= 10:
                break

        if len(recommended_products) < 10:
            for category_id in sorted_categories:
                additional_products = Product.objects.filter(category_id=category_id).exclude(id__in=viewed_product_ids)
                recommended_products.extend(additional_products)

                if len(recommended_products) >= 10:
                    break

        recommended_products = recommended_products[:10]
        random.shuffle(recommended_products)

        serializer = ProductSerializer(recommended_products, many=True, context={'request': request})
        return Response(serializer.data)
