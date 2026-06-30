from django.contrib import admin
from .models import Post, CustomEmoji, Comment, CommentVote, EmojiPack


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created_at')
    list_filter = ('published',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


class CustomEmojiInline(admin.TabularInline):
    model = CustomEmoji
    extra = 3


@admin.register(EmojiPack)
class EmojiPackAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    inlines = [CustomEmojiInline]


@admin.register(CustomEmoji)
class CustomEmojiAdmin(admin.ModelAdmin):
    list_display = ('name', 'pack')
    list_filter = ('pack',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'vote')