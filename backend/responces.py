from rest_framework.response import Response
from rest_framework import status


def field_errors_response(serializer, status_code=status.HTTP_400_BAD_REQUEST):
    error_list = []

    if 'non_field_errors' in serializer.errors:
        return error_response(serializer.errors['non_field_errors'][0], status_code)

    for field, errors in serializer.errors.items():
        field_name = field
        if field_name in serializer.fields:
            field_name = serializer.fields[field_name].source
        error_list.append({"title": field_name, "message": errors[0]})
    response_data = {
        "detail": error_list
    }
    return Response(response_data, status=status_code)


def error_response(message, error_code=status.HTTP_400_BAD_REQUEST):
    error_message = [{"message": message}]
    response_data = {"detail": error_message}
    response = Response(response_data, status=error_code)

    if error_code == status.HTTP_404_NOT_FOUND:
        setattr(response, 'is_custom_404', True)
    return response


def success_response(message, success_code=status.HTTP_200_OK):
    response_data = {
        "message": message
    }
    return Response(response_data, status=success_code)
