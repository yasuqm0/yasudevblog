from rest_framework import generics
from .models import Pagina, PerfilPromocionado
from .serializers import PaginaSerializer, PerfilPromocionadoSerializer


class PaginaDetailView(generics.RetrieveAPIView):
    queryset = Pagina.objects.all()
    serializer_class = PaginaSerializer
    lookup_field = 'slug'


class PerfilPromocionadoListView(generics.ListAPIView):
    queryset = PerfilPromocionado.objects.all()
    serializer_class = PerfilPromocionadoSerializer