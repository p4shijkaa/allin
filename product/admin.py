from django.contrib import admin
from product.models import Service, Flowers, Establishment, Dish, Taxi, Review, Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Image."""
    list_display = ["src", "alt"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Service."""

    list_display = ["id", "name", "description", "photo", "discount", "dateFrom",   # Поля отображаемые в админке
                    "dateTo", "comment", "is_active", "publish"]
    list_filter = ["name", "discount", "comment", "is_active", "publish"]   # Фильтрации по указанным полям
    search_fields = ["name", "description", "comment"]   # Поле поиска по указанным полям
    ordering = ["id", "publish"]   # Упорядочивание по умолчанию
    exclude = ["publish",]   # Поля исключены из редактируемых


@admin.register(Flowers)
class FlowersAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Flowers."""

    list_display = ["id", "service", "name", "description", "photo", "count", "price",   # Поля отображаемые в админке
                    "comment", "is_active", "publish"]
    list_filter = ["service", "name", "count", "price", "comment", "is_active",   # Фильтрации по указанным полям
                   "publish"]
    search_fields = ["service", "name", "description", "comment"]   # Поле поиска по указанным полям
    ordering = ["id", "publish"]   # Упорядочивание по умолчанию
    exclude = ["publish",]   # Поля исключены из редактируемых


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Establishment."""

    list_display = ["id", "service", "name", "description", "photo", "address",   # Поля отображаемые в админке
                    "comment", "is_active", "publish"]
    list_filter = ["service", "name", "address", "comment", "is_active", "publish"]   # Фильтрации по указанным полям
    search_fields = ["service", "name", "description", "address", "comment"]   # Поле поиска по указанным полям
    ordering = ["id", "publish"]   # Упорядочивание по умолчанию
    exclude = ["publish",]   # Поля исключены из редактируемых


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Dish."""

    list_display = ["id", "establishment", "name", "description", "photo", "count",  # Поля отображаемые в админке
                    "price", "comment", "is_active", "publish"]
    list_filter = ["establishment", "name", "count", "price", "comment", "is_active",   # Фильтрации по указанным полям
                   "publish"]
    search_fields = ["establishment", "name", "description", "comment"]   # Поле поиска по указанным полям
    ordering = ["id", "publish"]   # Упорядочивание по умолчанию
    exclude = ["publish",]   # Поля исключены из редактируемых


@admin.register(Taxi)
class TaxiAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Taxi."""

    list_display = ["id", "service", "boarding_address", "dropoff_address", "date_time",  # Поля отображаемые в админке
                    "price", "comment", "is_active", "publish"]
    list_filter = ["service", "date_time", "price", "comment", "is_active",   # Фильтрации по указанным полям
                   "publish"]
    search_fields = ["service", "name", "description", "comment"]   # Поле поиска по указанным полям
    ordering = ["id", "publish"]   # Упорядочивание по умолчанию
    exclude = ["publish",]   # Поля исключены из редактируемых


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Review."""

    list_display = ["id", "author", "text", "rating", "data", "service", "is_active"]   # Поля отображаемые в админке
    list_filter = ["author", "rating", "data", "service", "is_active"]   # Фильтрации по указанным полям
    search_fields = ["author", "text", "service"]   # Поле поиска по указанным полям
    ordering = ["id",]   # Упорядочивание по умолчанию
    exclude = ["data",]   # Поля исключены из редактируемых
