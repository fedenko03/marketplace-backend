from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import User


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Номер телефона должен быть в формате: '+71234567890'. До 15 цифр."
            )
        ]
    )
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Zа-яА-ЯёЁ\s]+$',
                message="Имя пользователя может содержать только латинские и кириллические буквы и пробелы."
            )
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'country', 'city']

    def validate_username(self, value):
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError(
                "Имя пользователя должно содержать от 2 до 100 символов."
            )
        return value
