from django.urls import path
from .views import PaginaDetailView, PerfilPromocionadoListView

urlpatterns = [
    path('<slug:slug>/', PaginaDetailView.as_view(), name='pagina-detail'),
    path('perfiles/', PerfilPromocionadoListView.as_view(), name='perfil-list'),
]