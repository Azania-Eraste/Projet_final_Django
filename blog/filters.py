import django_filters
from .models import Categorie, Tag, Article

class ArticleFilter(django_filters.FilterSet):

    categorie = django_filters.ModelChoiceFilter(
        field_name='categorie',
        queryset=Categorie.objects.filter(statut=True),
        label='Categories'
    )

    titre = django_filters.CharFilter(field_name='titre', lookup_expr='icontains', label='Titre', placeholder='Search....')

    tag = django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.filter(statut=True),
        label='Tags'
    )

    date_de_publication = django_filters.DateFilter(field_name='date_de_publication', lookup_expr='gte', label='Publié après')

    class Meta:
        model = Article
        fields = ['categorie', 'titre', 'tag', 'date_de_publication']