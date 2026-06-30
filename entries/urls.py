from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry_list, name='entry_list'),
    path('api/', views.api_entry_list, name='api_entry_list'),
    path('api/<slug:slug>/', views.api_entry_detail, name='api_entry_detail'),
    path('<slug:slug>/', views.entry_detail, name='entry_detail'),
]