import random

from django.contrib.auth import login
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user_account_auth.models import User
from user_account_auth.serializers import RegistrationSerializer, LoginUserSerializer, PasswordResetSerializer, \
    SetPasswordSerializer, VerificationSerializer, UserDetailsSerializer, GoogleLoginSerializer

auth_header_parameter = OpenApiParameter(
    name="Authorization",
    location=OpenApiParameter.HEADER,
    description="Токен авторизации в формате: Token <токен пользователя>",
    required=True)



@extend_schema_view(post=extend_schema(tags=["Пользователь: регистрация пользователя"]))
class UserRegistrationView(CreateAPIView):
    """
    Представление для регистрации пользователя.
    """

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"errors": {"email": ["Пользователь с таким email уже существует."]}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Пользователь неактивен до подтверждения почты
            # send_verification_code(user)
            request.session['email'] = user.email
            return Response({"message": "Код подтверждения отправлен на вашу почту."},
                            status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(GenericAPIView):
    """
    Представление для входа пользователей.
    """
    serializer_class = LoginUserSerializer

    @extend_schema(tags=["Пользователь: вход пользователя"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            if user:
                # Создаем или получаем токен для пользователя
                # token, created = Token.objects.get_or_create(user=user)
                # return Response({"message": 'Успешный вход.', "token": token.key, "id": user.pk},
                #                 status=status.HTTP_200_OK)
                # else:
                return Response({"errors": 'Неверные учетные данные.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(GenericAPIView):
    """
    Представление для выхода пользователей.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Пользователь: выход пользователя"],
                   parameters=[auth_header_parameter])
    def post(self, request, *args, **kwargs):
        try:
            # Получаем и удаляем токен пользователя
            request.user.auth_token.delete()
            return Response({"message": "Успешный выход из системы."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"errors": "Токен не найден или уже был удален."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(GenericAPIView):
    """
    Представление для восстановления пароля, с высылкой сгенерированного кода на почту.
    """

    serializer_class = PasswordResetSerializer

    @extend_schema(tags=["Пользователь: восстановления пароля через email"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"errors": "Пользователь с такой электронной почтой не найден."},
                                status=status.HTTP_404_NOT_FOUND)

            # send_verification_code(user)

            # # Сохраняем email и код в сессии
            # request.session['reset_email'] = email
            # request.session['reset_code'] = user.reset_code
            return Response({"message": "Код отправлен на вашу электронную почту."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(GenericAPIView):
    """
    Представление для сброса пароля и вводом нового.
    """
    serializer_class = SetPasswordSerializer

    @extend_schema(tags=["Пользователь: подтверждение сброса пароля"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пароль успешно обновлен."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(GenericAPIView):
    """
    Представление для удаления пользователя.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Пользователь: удаление пользователя"],
                   parameters=[auth_header_parameter])
    def delete(self, request):
        user = request.user

        # Удаление токенов пользователя
        Token.objects.filter(user=user).delete()
        # Удаление пользователя
        user.delete()
        return Response({"message": "Пользователь успешно удален."}, status=status.HTTP_204_NO_CONTENT)


class UserDetailsView(GenericAPIView):
    """
    Представление для просмотра(get)/редактирования информации о пользователе (patch).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailsSerializer

    @extend_schema(tags=["Пользователь: просмотр информации о пользователе"],
                   parameters=[auth_header_parameter])
    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response({"message": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(tags=["Пользователь: редактирование информации о пользователе"],
                   parameters=[auth_header_parameter])
    def patch(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": serializer.data}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(GenericAPIView):
    """
    Представление для входа пользователей через google аккаунт.
    """
    serializer_class = GoogleLoginSerializer

    @extend_schema(tags=["Пользователь: вход через google аккаунт"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        google_id = serializer.validated_data.get('google_id')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name)
            user.set_unusable_password()
            user.is_active = True
            user.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({"message": "Успешный вход через google аккаунт.", "token": token.key, "id": user.pk},
                        status=status.HTTP_200_OK)
