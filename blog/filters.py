from .models import Article, Categorie, Tag
import django_filters

class ArticleFilter(django_filters.FilterSet):
    categorie = django_filters.ModelChoiceFilter(
        field_name='categorie_id',
        queryset=Categorie.objects.filter(statut=True),
        label='Catégories',
        empty_label="Toutes les catégories"
    )

    titre = django_filters.CharFilter(
        field_name='titre',
        lookup_expr='icontains',
        label='Titre',
    )

    tag = django_filters.ModelMultipleChoiceFilter(
        field_name='tag_ids',
        queryset=Tag.objects.filter(statut=True),
        label='Tags',
    )

    date_de_publication = django_filters.DateFilter(
        field_name='date_de_publicatio',
        lookup_expr='gte',
        label='Publié après',
    )

    class Meta:
        model = Article
        fields = ['categorie', 'titre', 'tag', 'date_de_publication']

