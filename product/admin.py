from django.contrib import admin
from django.utils.html import format_html
from product.models import Service, Flowers, Establishment, Dish, Taxi, Review, Image, Decoration, City


def photo(obj):
    if obj.photo:
        return format_html('<a href="{}" target="_blank"><img src="{}" height="50" /></a>',
                           obj.photo.src.url, obj.photo.src.url)
    return "No Image"


photo.short_description = 'Фото'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Image."""
    list_display = ["src", "alt"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Service."""

    list_display = ["id", "name", "description", "photo", "discount", "dateFrom",  # Поля отображаемые в админке
                    "dateTo", "comment", "is_active", "publish"]
    list_filter = ["name", "discount", "comment", "is_active", "publish"]  # Фильтрации по указанным полям
    search_fields = ["name", "description", "comment"]  # Поле поиска по указанным полям
    ordering = ["id", "publish"]  # Упорядочивание по умолчанию
    exclude = ["publish", ]  # Поля исключены из редактируемых


@admin.register(Flowers)
class FlowersAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Flowers."""

    list_display = ["id", "service", "name", "description", "photo_url", "count", "price",
                    # Поля отображаемые в админке
                    "comment", "is_active", "publish"]
    list_filter = ["service", "name", "count", "price", "comment", "is_active",  # Фильтрации по указанным полям
                   "publish"]
    search_fields = ["service", "name", "description", "comment"]  # Поле поиска по указанным полям
    ordering = ["id", "publish"]  # Упорядочивание по умолчанию
    exclude = ["publish", ]  # Поля исключены из редактируемых

    def photo_url(self, obj):
        return photo(obj)

    photo_url.short_description = 'Фото цветов'


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Establishment."""

    list_display = ["id", "service", "name", "description", "photo_url", "address",  # Поля отображаемые в админке
                    "comment", "is_active", "publish", "city"]
    list_filter = ["service", "name", "address", "comment", "is_active", "publish", "city"]  # Фильтрации по указанным полям
    search_fields = ["service", "name", "description", "address", "comment", "city"]  # Поле поиска по указанным полям
    ordering = ["id", "publish"]  # Упорядочивание по умолчанию
    exclude = ["publish", ]  # Поля исключены из редактируемых

    def photo_url(self, obj):
        return photo(obj)

    photo_url.short_description = 'Фото заведения'


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Dish."""

    list_display = ["id", "establishment", "name", "description", "photo_url", "count",  # Поля отображаемые в админке
                    "price", "comment", "is_active", "publish"]
    list_filter = ["establishment", "name", "count", "price", "comment", "is_active",  # Фильтрации по указанным полям
                   "publish"]
    search_fields = ["establishment", "name", "description", "comment"]  # Поле поиска по указанным полям
    ordering = ["id", "publish"]  # Упорядочивание по умолчанию
    exclude = ["publish", ]  # Поля исключены из редактируемых

    def photo_url(self, obj):
        return photo(obj)

    photo_url.short_description = 'Фото блюда'


@admin.register(Taxi)
class TaxiAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Taxi."""

    list_display = ["id", "service", "boarding_address", "dropoff_address", "date_time",  # Поля отображаемые в админке
                    "price", "comment", "is_active", "publish"]
    list_filter = ["service", "date_time", "price", "comment", "is_active",  # Фильтрации по указанным полям
                   "publish"]
    search_fields = ["service", "name", "description", "comment"]  # Поле поиска по указанным полям
    ordering = ["id", "publish"]  # Упорядочивание по умолчанию
    exclude = ["publish", ]  # Поля исключены из редактируемых


@admin.register(Decoration)
class DecorationAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Decoration."""
    list_display = ["id", "service", "name", "description", "photo_url", "comment", 'price',
                    # Поля отображаемые в админке
                    "is_active", "publish"]
    list_filter = ["service", "name", "comment", 'price', "is_active", "publish"]  # Фильтрации по указанным полям
    search_fields = ["service", "name", "description", "comment"]  # Поле поиска по указанным полям
    ordering = ["id", "publish"]  # Упорядочивание по умолчанию
    exclude = ["publish", ]  # Поля исключены из редактируемых

    def photo_url(self, obj):
        return photo(obj)

    photo_url.short_description = 'Фото оформления'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Review."""

    list_display = ["id", "author_link", "text", "rating", "data", "service", "is_active"]  # Поля отображаемые в админке
    list_filter = ["author", "rating", "data", "service", "is_active"]  # Фильтрации по указанным полям
    search_fields = ["author", "text", "service"]  # Поле поиска по указанным полям
    ordering = ["id", ]  # Упорядочивание по умолчанию
    exclude = ["data", ]  # Поля исключены из редактируемых
    list_display_links = ["author_link"]  # Делаем поле author_link кликабельным

    def author_link(self, obj):
        if obj.author:
            return format_html('<a href="/admin/user_account_auth/user/{}/change/">{}</a>',
                               obj.author.id, obj.author.first_name or obj.author.email)
        return "Нет автора"
    author_link.short_description = 'Имя пользователя'
    author_link.admin_order_field = 'author'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели City."""

    list_display = ["id", "name"]  # Поля отображаемые в админке
    list_filter = ["name", ]  # Фильтрации по указанным полям
    search_fields = ["name", ]  # Поле поиска по указанным полям
    ordering = ["id", ]  # Упорядочивание по умолчанию
