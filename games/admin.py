from django.contrib import admin
from .models import Game, Achievement, PlayerAchievement

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'disc_reward')

@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ('player', 'achievement', 'earned_at')