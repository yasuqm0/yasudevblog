from django.contrib import admin
from .models import Entry, EntrySecret


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'template_type', 'active', 'access_hour_start', 'access_hour_end')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(EntrySecret)
class EntrySecretAdmin(admin.ModelAdmin):
    list_display = ('entry', 'trigger', 'achievement')