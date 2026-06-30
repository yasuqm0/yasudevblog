from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Game, Achievement, PlayerAchievement
from .serializers import GameSerializer
from accounts.models import Profile


def game_list(request):
    games = Game.objects.filter(active=True)
    return render(request, 'games/game_list.html', {'games': games})


def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug, active=True)
    achievements = game.achievements.all()
    unlocked = []
    if request.user.is_authenticated:
        unlocked = PlayerAchievement.objects.filter(
            player=request.user,
            achievement__game=game
        ).values_list('achievement_id', flat=True)
    return render(request, 'games/game_detail.html', {
        'game': game,
        'achievements': achievements,
        'unlocked': unlocked,
    })

def buscasemillas_view(request):
    return render(request, 'games/buscasemillas.html')

@login_required
def unlock_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id)
    already_unlocked = PlayerAchievement.objects.filter(
        player=request.user,
        achievement=achievement
    ).exists()
    if not already_unlocked:
        PlayerAchievement.objects.create(
            player=request.user,
            achievement=achievement
        )
        profile = request.user.profile
        profile.discs += achievement.disc_reward
        profile.save()
    return redirect('game_detail', slug=achievement.game.slug)

@api_view(['GET'])
def api_game_list(request):
    games = Game.objects.filter(active=True)
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)