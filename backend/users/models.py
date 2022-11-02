from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        db_index=True,
        unique=True,
        null=False,
        blank=False,
        max_length=254,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        db_index=True,
        unique=True,
        null=False,
        blank=False,
        max_length=150,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        blank=False,
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=False,
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username', 'email']

    def __str__(self):
        return self.username
