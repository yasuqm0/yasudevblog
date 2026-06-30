from rest_framework import serializers
from .models import Post, Comment, CommentVote, EmojiPack, CustomEmoji


class CommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentVote
        fields = ['id', 'user', 'vote']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'likes', 'dislikes']

    def get_likes(self, obj):
        return obj.votes.filter(vote=CommentVote.LIKE).count()

    def get_dislikes(self, obj):
        return obj.votes.filter(vote=CommentVote.DISLIKE).count()


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'created_at', 'image']


class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'image', 'created_at', 'updated_at', 'comments']


class CustomEmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomEmoji
        fields = ['id', 'name', 'image']


class EmojiPackSerializer(serializers.ModelSerializer):
    emojis = CustomEmojiSerializer(many=True, read_only=True)

    class Meta:
        model = EmojiPack
        fields = ['id', 'name', 'order', 'emojis']