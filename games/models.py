from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Achievement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='achievement')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    disc_reward = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name} ({self.game.title})'

class PlayerAchievement(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'achievement')
    
    def __str__(self):
        return f'{self.player.username} - {self.achievement.name}'