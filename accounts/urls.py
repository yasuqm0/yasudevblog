from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile, name='profile'),
    path('perfil/editar/', views.edit_profile, name='edit_profile'),
     path('api/perfil/', views.api_profile_detail, name='api_profile_detail'),
    path('usuario/<str:username>/', views.public_profile, name='public_profile'),
]