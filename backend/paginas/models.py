from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models


class Platform(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    icono = models.ImageField(upload_to='platform_icons/', blank=True, null=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class SocialLink(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    plataforma = models.ForeignKey(Platform, on_delete=models.PROTECT)
    username = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def clean(self):
        if not self.username and not self.url:
            raise ValidationError('Debes completar al menos el nombre de usuario o la URL.')

    def __str__(self):
        return f"{self.plataforma}: {self.username or self.url}"


class Pagina(models.Model):
    slug = models.SlugField(unique=True)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    links = GenericRelation(SocialLink)

    def __str__(self):
        return self.titulo


class PerfilPromocionado(models.Model):
    ROL_CHOICES = (
        ('yo', 'Yo'),
        ('artista', 'Artista'),
        ('programador', 'Programador'),
        ('amigo', 'Amigo'),
        ('otro', 'Otro'),
    )

    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    descripcion = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='perfiles_promocionados/', blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)

    links = GenericRelation(SocialLink)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.nombre