import logging

from django.contrib.auth import get_user_model, authenticate
from django.core.validators import EmailValidator
from rest_framework import serializers
from user_account_auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'email', 'password1', 'password2')

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают")
        email = data['email'].lower()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            if user.is_active:
                raise serializers.ValidationError("Пользователь с такой почтой уже существует и активен.")
            else:
                user.delete()
        return data

    def create(self, validated_data):
        # Удаляем поля password1 и password2 из validated_data
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        # Создаем пользователя с оставшимися данными
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False  # Пользователь деактивирован до подтверждения почты
        user.save()
        return user


class VerificationSerializer(serializers.Serializer):
    """
    Сериализатор для верификации пользователя.
    """
    code = serializers.CharField(max_length=5)
    email = serializers.EmailField()  # новая строка тест
    def validate(self, data):
        code = data.get('code')
        email = self.context['request'].data.get('email')   # новая строка тест
        print(f"111 code: {code}")
        print(f"222 email: {email}")
        # email = self.context['request'].session.get('email')

        if not email:
            raise serializers.ValidationError("Email для подтверждения не найден в сессии.")

        user = User.objects.filter(email=email, reset_code=code, is_active=False).first()
        if not user:
            raise serializers.ValidationError("Неверный код подтверждения.")

        data['user'] = user
        print(user.email)
        return data


class LoginUserSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователей.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Неверные учетные данные.")
            data['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать имя пользователя и пароль.")
        return data


class PasswordResetSerializer(serializers.Serializer):
    """
    Сериализатор для восстановления пароля.
    """
    email = serializers.EmailField()


class SetPasswordSerializer(serializers.Serializer):
    """
    Сериализатор для сброса пароля с помощью высланного кода на Email.
    """
    code = serializers.CharField(max_length=5)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def save(self):
        code = self.validated_data['code']
        new_password = self.validated_data['new_password1']
        email = self.context['request'].session.get('reset_email')

        if not email:
            raise serializers.ValidationError({"errors": "Email для сброса пароля не найден в сессии."})

        user = User.objects.get(email=email)
        if not user:
            raise serializers.ValidationError({"errors": "Пользователь с таким email не найден."})

        # Проверяем код из сессии
        if self.context['request'].session.get('reset_code') != code:
            raise serializers.ValidationError({"errors": "Неверный код сброса пароля."})

        user.reset_code = None
        user.set_password(new_password)
        user.save()
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра/редактирования информации о пользователе.
    """
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'phone', 'date_joined', 'about_me', 'city', 'is_active')
        read_only_fields = ('date_joined', 'is_active')


class GoogleLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователей через google аккаунт.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    google_id = serializers.CharField()
