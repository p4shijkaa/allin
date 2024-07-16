from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from user_account_auth.models import User


class Image(models.Model):
    """Модель для хранения изображений."""

    src = models.ImageField(upload_to="static/image/", default="static/image/default.png", verbose_name="Ссылка")
    alt = models.CharField(max_length=128, verbose_name="Описание")

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.alt if self.src else "No Image"


class Service(models.Model):
    """Модель Service представляет услуги, предлагаемые на платформе."""
    name = models.CharField(max_length=100, verbose_name="Название услуги")
    description = models.TextField(null=True, blank=True, verbose_name="Описание услуги")
    photo = models.ForeignKey(Image, on_delete=models.SET_NULL, related_name="service_photo", blank=True, null=True,
                              verbose_name="Фото услуги")
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0,
                                   verbose_name="Скидка на услугу")
    dateFrom = models.DateTimeField(null=True, blank=True, verbose_name="Дата начала акции")
    dateTo = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания акции")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заказу")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    def calculate_total_price(self):
        """Высчитываем цену за услугу, с учётом выбора пользователя"""
        total_price = 0
        for flower in self.flowers.all():
            total_price += flower.price
        for establishment in self.establishments.all():
            for dish in establishment.dishes.all():
                total_price += dish.price
        for taxi in self.taxis.all():
            total_price += taxi.price

        discount = (self.discount / 100) * total_price
        total_price -= discount
        return total_price

    @property
    def price(self):
        return self.calculate_total_price()

    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.name


class Flowers(models.Model):
    """Модель цветы для услуг."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='flowers')
    name = models.CharField(max_length=100, verbose_name="Название букета")
    description = models.TextField(null=True, blank=True, verbose_name="Информация о букете")
    photo = models.ForeignKey(Image, on_delete=models.SET_NULL, related_name="flowers_photo", blank=True, null=True,
                              verbose_name="Фото букета")
    count = models.IntegerField(null=True, blank=True, verbose_name="Количество цветов в букете")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена букета")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к букету")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Цветы"
        verbose_name_plural = "Цветы"

    def __str__(self):
        return self.name


class Establishment(models.Model):
    """Модель заведение(кафе, ресторан) для услуг."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='establishments')
    name = models.CharField(max_length=100, verbose_name="Название заведения")
    description = models.TextField(null=True, blank=True, verbose_name="Информация о заведении")
    photo = models.ForeignKey(Image, on_delete=models.SET_NULL, related_name="establishment_photo", blank=True,
                              null=True, verbose_name="Фото заведения")
    address = models.CharField(max_length=100, verbose_name="Адрес заведения")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заведению")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заведение"
        verbose_name_plural = "Заведения"

    def __str__(self):
        return self.name


class Dish(models.Model):
    """Модель блюд для заведения."""
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    description = models.TextField(null=True, blank=True, verbose_name="Информация о блюде")
    photo = models.ForeignKey(Image, on_delete=models.SET_NULL, related_name="dish_photo", blank=True, null=True,
                              verbose_name="Фото блюда")
    count = models.IntegerField(default=1, verbose_name="Количество блюд")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена блюда")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к блюду")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюдо"

    def __str__(self):
        return self.name


class Taxi(models.Model):
    """Модель такси для услуги"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='taxis')
    boarding_address = models.CharField(max_length=255, verbose_name="Адрес посадки пассажира")
    dropoff_address = models.CharField(max_length=255, verbose_name="Адрес высадки пассажира")
    date_time = models.DateTimeField(verbose_name="Дата и время для подачи такси")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена такси")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к такси")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Такси"
        verbose_name_plural = "Такси"

    def __str__(self):
        return self.service.name


class Review(models.Model):
    """Модель Review представляет отзывы пользователей об услуге."""

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name="reviews",
                               verbose_name="Имя пользователя")
    text = models.TextField(verbose_name="Отзыв")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=5, verbose_name="Рейтинг")
    data = models.DateTimeField(default=timezone.now)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="reviews", verbose_name="Услуга")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.is_active
