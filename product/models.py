from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from user_account_auth.models import User


class Product(models.Model):
    """Модель Product представляет услуги, предлагаемые на платформе."""
    pass


class Review(models.Model):
    """Модель Review представляет отзывы пользователей об услуге."""

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name="reviews",
                               verbose_name="Имя пользователя")
    text = models.TextField(verbose_name="Отзыв")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=0, verbose_name="Рейтинг", )
    data = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Продукт")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text
