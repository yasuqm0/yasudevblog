from rest_framework import serializers
from .models import Entry


class EntrySerializer(serializers.ModelSerializer):
    """Para listar entradas: nunca expone el contenido."""
    is_accessible = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ['id', 'title', 'slug', 'template_type', 'active',
                  'access_hour_start', 'access_hour_end', 'created_at', 'is_accessible']

    def get_is_accessible(self, obj):
        return obj.is_accessible()


class EntryDetailSerializer(serializers.ModelSerializer):
    """Solo se usa cuando ya se confirmó que la entrada es accesible."""
    class Meta:
        model = Entry
        fields = ['id', 'title', 'slug', 'content', 'template_type', 'created_at']