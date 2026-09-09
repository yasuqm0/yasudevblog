from django.contrib import admin
from .models import Tag, Post, PostImage, PostReaction, Comment, CommentReaction, CustomEmoji


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha_publicacion', 'vistas')
    list_filter = ('tags',)
    search_fields = ('titulo', 'contenido')
    inlines = [PostImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('autor', 'post', 'fecha_creacion', 'respuesta_a')
    list_filter = ('post',)


admin.site.register(Tag)
admin.site.register(PostReaction)
admin.site.register(CommentReaction)
admin.site.register(CustomEmoji)