import random
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from user_account_auth.models import User
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from user_account_auth.serializers import RegistrationSerializer, LoginUserSerializer, PasswordResetSerializer, \
    SetPasswordSerializer, VerificationSerializer, UserDetailsSerializer

auth_header_parameter = OpenApiParameter(
    name="Authorization",
    location=OpenApiParameter.HEADER,
    description="Токен авторизации в формате: Token <токен пользователя>",
    required=True)


def send_verification_code(user):
    code = ''.join(random.choices('0123456789', k=5))  # Генерируем код для пользователя
    user.reset_code = code  # Сохраняем код в поле пользователя
    user.save()

    # Отправляем новый пароль на электронную почту пользователя
    send_mail(
        'Подтверждение почты',
        f'Ваш код подтверждения: {code}',
        'e.v.solovey@inbox.ru',  # Замените на вашу электронную почту
        [user.email],
        fail_silently=False,
    )


@extend_schema_view(post=extend_schema(tags=["Регистрация пользователя"]))
class UserRegistrationView(CreateAPIView):
    """
    Представление для регистрации пользователя.
    """

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Пользователь неактивен до подтверждения почты
            send_verification_code(user)
            request.session['email'] = user.email
            return Response({"message": "Код подтверждения отправлен на вашу почту."},
                            status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(GenericAPIView):
    """
    Представление для подтверждения почты и активации пользователя.
    """

    serializer_class = VerificationSerializer

    @extend_schema(tags=["Подтверждение регистрации"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.reset_code = None
            user.save()

            # Создаем или получаем токен для пользователя
            token, created = Token.objects.get_or_create(user=user)

            # Выполняем вход пользователя
            login(request, user)
            # Удаляем данные из сессии
            if 'email' in request.session:
                del request.session['email']

            return Response({"message": "Регистрация успешно подтверждена.", "token": token.key, "id": user.pk},
                            status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
                return Response({"message": 'Успешный вход.', "token": token.key, "id": user.pk},
                                status=status.HTTP_200_OK)
            else:
                return Response({"errors": 'Неверные учетные данные.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(GenericAPIView):
    """
    Представление для выхода пользователей.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Выход пользователя"],
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

    @extend_schema(tags=["Восстановления пароля через email"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"errors": serializer.errors},
                                status=status.HTTP_404_NOT_FOUND)

            send_verification_code(user)

            # Сохраняем email и код в сессии
            request.session['reset_email'] = email
            request.session['reset_code'] = user.reset_code
            return Response({"message": "Код отправлен на вашу электронную почту."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(GenericAPIView):
    """
    Представление для сброса пароля и вводом нового.
    """
    serializer_class = SetPasswordSerializer

    @extend_schema(tags=["Подтверждение сброса пароля"])
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Удаляем email и код из сессии после успешного сброса пароля
            del request.session['reset_email']
            del request.session['reset_code']
            return Response({"message": "Пароль успешно обновлен."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(GenericAPIView):
    """
    Представление для удаления пользователя.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Удаление пользователя"],
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

    @extend_schema(tags=["Просмотр информации о пользователе"],
                   parameters=[auth_header_parameter])
    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response({"message": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(tags=["Редактирование информации о пользователе"],
                   parameters=[auth_header_parameter])
    def patch(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": serializer.data}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
