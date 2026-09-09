from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(blank=True)
    display_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    chip_anomalo = models.PositiveIntegerField(default=0)
    nucleo_singularidad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username