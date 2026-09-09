from rest_framework import serializers
from .models import Tag, Post, PostImage, Comment, CustomEmoji


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'nombre', 'slug')


class AutorSerializer(serializers.Serializer):
    username = serializers.CharField()
    display_name = serializers.CharField()
    avatar = serializers.ImageField()


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'imagen', 'fecha_subida')


class CommentSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    respuestas = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'autor', 'contenido', 'fecha_creacion', 'respuesta_a', 'respuestas')

    def get_respuestas(self, obj):
        return CommentSerializer(obj.respuestas.all(), many=True).data


class PostListSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'titulo', 'slug', 'autor', 'fecha_publicacion', 'vistas', 'tags')


class PostDetailSerializer(PostListSerializer):
    imagenes = PostImageSerializer(many=True, read_only=True)
    comentarios = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ('contenido', 'imagenes', 'comentarios')

    def get_comentarios(self, obj):
        raiz = obj.comentarios.filter(respuesta_a__isnull=True)
        return CommentSerializer(raiz, many=True).data