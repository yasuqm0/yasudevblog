from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class EmojiPack(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class CustomEmoji(models.Model):
    pack = models.ForeignKey(EmojiPack, on_delete=models.CASCADE, related_name='emojis', null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    image = models.FileField(upload_to='emojis/')

    def __str__(self):
        return f':{self.name}:'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} en {self.post.title}'

class CommentVote(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f'{self.user.username} → {self.vote} en comentario {self.comment.id}'