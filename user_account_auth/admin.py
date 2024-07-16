from django.contrib import admin
from user_account_auth.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели User."""

    list_display = ["id", "first_name", "last_name", "email", "phone", "date_joined",   # Поля отображаемые в админке
                    "about_me", "photo", "city", "is_active", "is_staff", "is_verified"]
    list_filter = ["id", "first_name", "last_name", "date_joined", "city", "is_active"]  # Фильтрации по указанным полям
    search_fields = ["first_name", "last_name", "email", "phone", "city"]   # Поле поиска по указанным полям
    ordering = ["id",]   # Упорядочивание по умолчанию
    exclude = ["date_joined",]   # Поля исключены из редактируемых
