from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
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
    reset_code = models.CharField(max_length=150, null=True, blank=True, verbose_name='Код для сброса пароля')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        unique_together = ('email', 'phone')

    def __str__(self):
        return self.email or f"Пользователь {self.id}"
