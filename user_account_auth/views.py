import random
from django.contrib.auth import login, authenticate, logout
from rest_framework.permissions import IsAuthenticated
from user_account_auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from user_account_auth.serializers import RegistrationSerializer, LoginUserSerializer, PasswordResetSerializer, \
    SetPasswordSerializer


@extend_schema_view(post=extend_schema(tags=["Регистрация пользователя"]))
class UserRegistrationView(CreateAPIView):
    """
    Представление для регистрации пользователей с подтверждением почты.
    """

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                return Response({"message": "Пользователь с такой почтой уже существует."},
                                status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            base_url = request.build_absolute_uri('/')[:-1]
            verification_link = f"{base_url}/auth/verify-email/{uid}/{token}"

            # Отправляем письмо с подтверждением
            send_mail(
                'Подтверждение почты',
                f'Пожалуйста, подтвердите свою почту, перейдя по ссылке: {verification_link}',
                'e.v.solovey@inbox.ru',  # Замените на вашу электронную почту
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "Письмо с подтверждением отправлено на вашу почту."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(GenericAPIView):
    """
    Представление для подтверждения почты и активации пользователя.
    """

    @extend_schema(tags=["Подтверждение почты"])
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None:
            if user.is_active:
                # Если пользователь уже активирован, получаем его токен
                token = Token.objects.get(user=user)
                return Response({
                    "message": "Пользователь уже активирован.",
                    "token": token.key,
                }, status=status.HTTP_200_OK)
            elif default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()

                # Создаем или получаем токен для пользователя
                token, created = Token.objects.get_or_create(user=user)

                # Логиним пользователя
                login(request, user)

                return Response({
                    "message": "Почта успешно подтверждена.",
                    "token": token.key,
                    "email": user.email
                }, status=status.HTTP_200_OK)
        return Response({"error": "Неверный токен или пользователь не найден."}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(GenericAPIView):
    """
    Представление для входа пользователей.
    """
    serializer_class = LoginUserSerializer

    @extend_schema(tags=["Вход пользователя"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            if user:
                # Создаем или получаем токен для пользователя
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'detail': 'Успешный вход.',
                    'token': token.key
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неверные учетные данные.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(GenericAPIView):
    """
    Представление для выхода пользователей.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Выход пользователя"])
    def post(self, request, *args, **kwargs):
        # Получаем токен пользователя
        token = Token.objects.get(user=self.request.user)
        if token:
            # Удаляем токен из базы данных
            token.delete()
            return Response({"detail": "Успешный выход из системы."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Токен не найден."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(GenericAPIView):
    """
    Представление для восстановления пароля, с высылкой сгенерированного кода на почту.
    """

    serializer_class = PasswordResetSerializer

    @extend_schema(tags=["Восстановления пароля через email"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "Пользователь с такой электронной почтой не найден."},
                                status=status.HTTP_404_NOT_FOUND)

            code = ''.join(random.choices('0123456789', k=5))  # Генерируем код для пользователя
            user.reset_code = code  # Сохраняем код в поле пользователя
            user.save()

            # Отправляем новый пароль на электронную почту пользователя
            send_mail(
                'Сброс пароля',
                f'Ваш код для сброса пароля: {code}',
                'e.v.solovey@inbox.ru',  # Замените на вашу электронную почту
                [email],
                fail_silently=False,
            )

            # Сохраняем email и код в сессии
            request.session['reset_email'] = email
            request.session['reset_code'] = code
            return Response({"message": "Код отправлен на вашу электронную почту."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(GenericAPIView):
    """
    Представление для сброса пароля и вводом нового.
    """
    serializer_class = SetPasswordSerializer

    @extend_schema(tags=["Подтверждение сброса пароля"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Удаляем email и код из сессии после успешного сброса пароля
            del request.session['reset_email']
            del request.session['reset_code']
            return Response({"message": "Пароль успешно обновлен."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
