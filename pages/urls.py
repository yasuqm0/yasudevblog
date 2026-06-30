from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sobre-mi/', views.about, name='about'),
    path('api/', views.api_index, name='api_index'),
    path('api/<slug:slug>/', views.api_page_detail, name='api_page_detail'),
]