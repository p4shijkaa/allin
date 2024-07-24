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
    email = serializers.EmailField()

    def validate(self, data):
        code = data.get('code')
        email = self.context['request'].data.get('email')

        if not email:
            raise serializers.ValidationError("Email для подтверждения не найден в сессии.")

        user = User.objects.filter(email=email, reset_code=code, is_active=False).first()
        if not user:
            raise serializers.ValidationError("Неверный код подтверждения.")

        data['user'] = user
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
            user = User.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("Неверные учетные данные.")
            if not user.is_active:
                user.delete()
                raise serializers.ValidationError(
                    "Ваш аккаунт не активирован. Пожалуйста, зарегистрируйтесь и подтвердите свою почту.")
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Неверные учетные данные.")
            data['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль.")
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
    email = serializers.EmailField()
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        code = data.get('code')
        email = self.context['request'].data.get('email')
        new_password1 = data.get('new_password1')
        new_password2 = data.get('new_password2')

        if new_password1 != new_password2:
            raise serializers.ValidationError("Пароли не совпадают.")
        if not email:
            raise serializers.ValidationError({"errors": "Email для сброса пароля не найден в сессии."})
        user = User.objects.filter(email=email, reset_code=code).first()
        if not user:
            raise serializers.ValidationError({"errors": "Неверный код сброса пароля."})
        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password1']

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
