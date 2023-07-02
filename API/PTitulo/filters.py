import django_filters
from .models import Anuncio, Reputacion, Mascota

class AnuncioFilter(django_filters.FilterSet):
    autor = django_filters.CharFilter(lookup_expr='exact')  # Filtro para el campo "autor" con coincidencia exacta
    contacto = django_filters.CharFilter(lookup_expr='exact')  # Filtro para el campo "contacto"

    class Meta:
        model = Anuncio
        fields = ['autor', 'contacto']  # Especifica los campos disponibles para el filtro

class ReputacionFilter(django_filters.FilterSet):
    usuario = django_filters.CharFilter(lookup_expr='exact')  # Filtro para el campo "autor" con coincidencia exacta
    evaluador = django_filters.CharFilter(lookup_expr='exact')  # Filtro para el campo "contacto"

    class Meta:
        model = Reputacion
        fields = ['usuario', 'evaluador']  # Especifica los campos disponibles para el filtro


class MascotaFilter(django_filters.FilterSet):
    dueno = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Mascota
        fields = ['dueno']  # Añade el campo de filtro personalizado a la lista de campos disponibles

