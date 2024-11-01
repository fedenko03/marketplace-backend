from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from backend.responces import field_errors_response
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Пользователь успешно зарегистрирован.", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return field_errors_response(serializer)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []


class RefreshTokenView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    authentication_classes = []
