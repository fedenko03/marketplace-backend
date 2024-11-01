from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.core.exceptions import ValidationError
import re

User = get_user_model()


def validate_password(value):
    if len(value) < 8 or len(value) > 20:
        raise ValidationError('Пароль должен содержать от 8 до 20 символов.')

    if not re.search(r'[a-z]', value):
        raise ValidationError('Пароль должен содержать хотя бы одну строчную букву.')

    if not re.search(r'[A-Z]', value):
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву.')

    if not re.search(r'[0-9]', value):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру.')

    if not re.search(r'[!@#$%^&,.?":]', value):
        raise ValidationError('Пароль должен содержать хотя бы один специальный символ: !@#$%^&,.?":')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        user = authenticate(username=attrs.get('email'), password=attrs.get('password'))
        if user is None:
            raise ValidationError('Неверный пароль или пользователя с такой почтой не существует.')

        data = super().validate(attrs)
        data['message'] = 'Login successful'
        data['role'] = user.role
        data['access_token'] = data.pop('access')
        data['refresh_token'] = data.pop('refresh')
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs['refresh'] = attrs.pop('refresh')
        return super().validate(attrs)