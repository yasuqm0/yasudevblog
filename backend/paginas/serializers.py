from rest_framework import serializers
from .models import Pagina, PerfilPromocionado, SocialLink, Platform


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('nombre', 'slug', 'icono')


class SocialLinkSerializer(serializers.ModelSerializer):
    plataforma = PlatformSerializer(read_only=True)

    class Meta:
        model = SocialLink
        fields = ('plataforma', 'username', 'url', 'orden')


class PaginaSerializer(serializers.ModelSerializer):
    links = SocialLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Pagina
        fields = ('slug', 'titulo', 'contenido', 'fecha_actualizacion', 'links')


class PerfilPromocionadoSerializer(serializers.ModelSerializer):
    links = SocialLinkSerializer(many=True, read_only=True)

    class Meta:
        model = PerfilPromocionado
        fields = ('id', 'nombre', 'rol', 'descripcion', 'avatar', 'orden', 'links')