from rest_framework.views import exception_handler
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException


def jwt_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if 'token_not_valid' in response.data.get('code', '').lower():
            response.data = {'ErrorMessages': [{'message': 'Токен доступа недействительный или устарел.'}]}
    return response


class IsAuthenticatedCustom(BasePermission):
    message = {
        "ErrorMessages": [
            {"message": "Зарегистрируйтесь пожалуйста."}
        ]
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise APIException(detail=self.message, code='authentication_failed')
        return True
