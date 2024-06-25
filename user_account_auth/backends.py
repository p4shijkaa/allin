from .models import User
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, email=None, password=None, **kwargs):

        try:
            user = User.objects.get(
                Q(email=email) | Q(phone=email)
            )

        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        else:
            return None
