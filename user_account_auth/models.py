from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from user_account_auth.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя, наследованная от базового класса Django."""
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Почта')
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name='Телефон')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    about_me = models.TextField(null=True, blank=True, verbose_name='О себе')
    photo = models.ImageField(upload_to='photos/', null=True, blank=True, verbose_name='Фото')
    city = models.CharField(max_length=150, null=True, blank=True, verbose_name='Город')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # groups = models.ManyToManyField(
    #     Group,
    #     verbose_name=_('groups'),
    #     blank=True,
    #     help_text=_(
    #         'The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
    #     related_name='users_set'
    # )
    # user_permissions = models.ManyToManyField(
    #     Permission,
    #     verbose_name=_('user permissions'),
    #     blank=True,
    #     help_text=_('Specific permissions for this user.'),
    #     related_name='users_set'
    # )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        unique_together = ('email', 'phone')
