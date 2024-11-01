import random

from django.db.models import Max
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from .models import Product, UserProductInteraction
from .serializers import ProductSerializer, UserProductInteractionSerializer
from .filters import ProductFilter
from .pagination import CustomPagination


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
    pagination_class = CustomPagination

    def get_queryset(self):
        liked_products = UserProductInteraction.objects.filter(
            user=self.request.user, interaction_type=UserProductInteraction.LIKE
        ).values_list('product', flat=True)
        return Product.objects.filter(id__in=liked_products)


class ViewedProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

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

        liked_categories = list(UserProductInteraction.objects.filter(
            user=user,
            interaction_type=UserProductInteraction.LIKE
        ).values_list('product__category', flat=True).distinct())

        viewed_categories = list(UserProductInteraction.objects.filter(
            user=user,
            interaction_type=UserProductInteraction.VIEW
        ).values_list('product__category', flat=True).distinct())

        category_ids = list(set(liked_categories + viewed_categories))

        viewed_product_ids = list(UserProductInteraction.objects.filter(
            user=user,
            interaction_type=UserProductInteraction.VIEW
        ).values_list('product_id', flat=True).distinct())

        recommended_products = Product.objects.filter(category_id__in=category_ids).exclude(id__in=viewed_product_ids)

        recommended_products = list(recommended_products)
        random.shuffle(recommended_products)

        recommended_products = recommended_products[:10]

        serializer = ProductSerializer(recommended_products, many=True, context={'request': request})
        return Response(serializer.data)
