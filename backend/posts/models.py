from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Post(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    contenido = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='posts')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    vistas = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='posts/%Y/%m/')
    fecha_subida = models.DateTimeField(auto_now_add=True)


class PostReaction(models.Model):
    TIPO_CHOICES = (('like', 'Like'), ('dislike', 'Dislike'))

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reacciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    class Meta:
        unique_together = ('post', 'usuario')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    respuesta_a = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')


class CommentReaction(models.Model):
    TIPO_CHOICES = (('like', 'Like'), ('dislike', 'Dislike'))

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reacciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    class Meta:
        unique_together = ('comment', 'usuario')


class CustomEmoji(models.Model):
    codigo = models.SlugField(max_length=30, unique=True)
    imagen = models.ImageField(upload_to='emojis/')

    def __str__(self):
        return f':{self.codigo}:'