from django.http import JsonResponse


def json_error_response(message, status):
    return JsonResponse({
        'ErrorMessages': [
            {'message': message}
        ]
    }, status=status)


def csrf_failure(request, reason=""):
    return json_error_response('Ошибка доступа.', 403)


def custom_404_view(request, exception=None):
    return json_error_response('Страница не найдена.', 404)


def custom_500_view(request):
    return json_error_response('Внутренняя ошибка сервера.', 500)
