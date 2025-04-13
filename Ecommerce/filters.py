# Ecommerce/filters.py
import django_filters
from .models import VariationProduit, CategorieProduit


class VariationProduitFilter(django_filters.FilterSet):
    prix_min = django_filters.NumberFilter(field_name='prix', lookup_expr='gte')
    prix_max = django_filters.NumberFilter(field_name='prix', lookup_expr='lte')
    categorie = django_filters.ModelChoiceFilter(
        field_name='produit__categorie',
        queryset=CategorieProduit.objects.filter(statut=True),
        label='Catégorie'
    )
    nom = django_filters.CharFilter(field_name='nom', lookup_expr='icontains', label='Nom')

    class Meta:
        model = VariationProduit
        fields = ['prix_min', 'prix_max', 'categorie', 'nom']

