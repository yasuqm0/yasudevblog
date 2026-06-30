from django.db import models
from games.models import Achievement


class Entry(models.Model):

    TEMPLATE_CHOICES = [
        ('full', 'Con layout completo'),
        ('minimal', 'Sin header ni footer'),
        ('blank', 'Página en blanco'),
        ('custom', 'Template personalizado'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='full')
    custom_template = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    access_hour_start = models.IntegerField(null=True, blank=True)
    access_hour_end = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_accessible(self):
        if self.access_hour_start is None:
            return True
        from datetime import datetime
        current_hour = datetime.now().hour
        if self.access_hour_start <= self.access_hour_end:
            return self.access_hour_start <= current_hour < self.access_hour_end
        else:
            return current_hour >= self.access_hour_start or current_hour < self.access_hour_end


class EntrySecret(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='secrets')
    achievement = models.ForeignKey(Achievement, on_delete=models.SET_NULL, null=True, blank=True)
    trigger = models.CharField(max_length=200)

    def __str__(self):
        return f'Secreto en {self.entry.title}'