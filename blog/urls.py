from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('api/', views.api_post_list, name='api_post_list'),
    path('api/<slug:slug>/', views.api_post_detail, name='api_post_detail'),
    path('<slug:slug>', views.post_detail, name='post_detail'),
    path('<slug:slug>/votar/<int:comment_id>/<str:vote_type>/', views.vote_comment, name='vote_comment'),
    path('<slug:slug>/eliminar-comentario/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]