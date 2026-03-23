from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    EmailField,
)

class User(AbstractUser):
    username = None
    email = EmailField(unique=True, verbose_name="Email")
    phone = CharField(max_length=35, verbose_name="Телефон", blank=True, null=True, help_text="Введите номер телефона")
    country = CharField(max_length=50, verbose_name="Страна", blank=True, null=True, help_text="Введите страну")
    chat_id = CharField(max_length=255, verbose_name="chat_id", blank=True, null=True, help_text="Введите ТГ ID")

    token = CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
