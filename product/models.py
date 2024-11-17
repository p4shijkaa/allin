from decimal import Decimal
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

    # def calculate_total_price(self):
    #     """Высчитываем цену за услугу, с учётом выбора пользователя"""
    #     total_price = Decimal('0.00')
    #
    #     for flower in self.flowers.all():
    #         total_price += Decimal(flower.price)
    #
    #     for establishment in self.establishments.all():
    #         for dish in establishment.dishes.all():
    #             total_price += Decimal(dish.price)
    #
    #     for taxi in self.taxis.all():
    #         total_price += Decimal(taxi.price)
    #
    #     for decoration in self.decorations.all():
    #         total_price += Decimal(decoration.price)
    #
    #     discount = (Decimal(self.discount) / Decimal('100.00')) * total_price
    #     total_price -= discount
    #     return total_price
    #
    # @property
    # def price(self):
    #     return self.calculate_total_price()

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
    city = models.ForeignKey('City', on_delete=models.SET_NULL, related_name="establishments", blank=True,
                             null=True, verbose_name="Город")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время начала"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата и время окончания"
    )
    total_tables = models.PositiveIntegerField(default=0, verbose_name="Общее количество столиков")

    opening_time = models.TimeField(verbose_name="Время открытия", default='10:00')
    closing_time = models.TimeField(verbose_name="Время закрытия", default='22:00')

    class Meta:
        verbose_name = "Заведение"
        verbose_name_plural = "Заведения"

    def __str__(self):
        return self.name


class Reservation(models.Model):
    """Модель для бронирования столиков."""
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='reservations')
    reserved_tables = models.PositiveIntegerField(default=1, verbose_name="Забронированные столики")
    reservation_time = models.DateTimeField(verbose_name="Дата и время бронирования")

    def save(self, *args, **kwargs):
        # Уменьшаем общее количество столиков при бронировании
        if self.establishment.total_tables >= self.reserved_tables:
            self.establishment.total_tables -= self.reserved_tables
            self.establishment.save()
        else:
            raise ValueError("Недостаточно столиков для бронирования.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирование"

    def __str__(self):
        return f"Бронирование у {self.establishment.name} на {self.reservation_time}"


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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('15.00'), verbose_name="Цена такси")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к такси")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Такси"
        verbose_name_plural = "Такси"

    def __str__(self):
        return self.service.name


class Decoration(models.Model):
    """Модель оформление для услуги"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='decorations')
    name = models.CharField(max_length=100, verbose_name="Название оформления")
    description = models.TextField(null=True, blank=True, verbose_name="Информация об оформлении")
    photo = models.ForeignKey(Image, on_delete=models.SET_NULL, related_name="decoration_photo", blank=True,
                              null=True, verbose_name="Фото оформления")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена оформления")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к оформлению")
    is_active = models.BooleanField(default=True, verbose_name="Активно/неактивно")
    publish = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Оформление"
        verbose_name_plural = "Оформления"

    def __str__(self):
        return self.name


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
        return self.author.first_name if self.author and self.author.first_name else self.author.email


class City(models.Model):
    """Модель City представляет информацию об городе заведения. Предназначена для фильтрации заведений по городу"""
    name = models.CharField(max_length=20, verbose_name='Название города')

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name
