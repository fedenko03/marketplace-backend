from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from backend.responces import field_errors_response
from .serializers import UpdateUserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'country': user.country,
            'city': user.city,
            'role': user.role,
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = UpdateUserProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Настройки профиля успешно обновлены"}, status=status.HTTP_200_OK)
        return field_errors_response(serializer)
