from rest_framework import serializers
from .models import Game, Achievement, PlayerAchievement


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'disc_reward']


class GameSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'title', 'slug', 'description', 'active', 'achievement']