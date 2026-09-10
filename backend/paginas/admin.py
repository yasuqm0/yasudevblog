from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Pagina, PerfilPromocionado, SocialLink, Platform


class SocialLinkInline(GenericTabularInline):
    model = SocialLink
    extra = 1


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')


@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'fecha_actualizacion')
    inlines = [SocialLinkInline]


@admin.register(PerfilPromocionado)
class PerfilPromocionadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rol', 'orden')
    list_filter = ('rol',)
    inlines = [SocialLinkInline]