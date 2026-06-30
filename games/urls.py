from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('buscasemillas/', views.buscasemillas_view, name='buscasemillas'),
    path('achievement/<int:achievement_id>/unlock/', views.unlock_achievement, name='unlock_achievement'),
    path('api/', views.api_game_list, name='api_game_list'),
    path('<slug:slug>/', views.game_detail, name='game_detail'),
]