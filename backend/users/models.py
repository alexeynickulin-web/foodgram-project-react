from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
            db_index=True,
            unique=True,
            null=False,
            blank=False,
            max_length=254,
        )
    username = models.CharField(
        db_index=True,
        unique=True,
        null=False,
        blank=False,
        max_length=150,
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
    )    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ['username', 'email']

    def __str__(self):
        return self.username