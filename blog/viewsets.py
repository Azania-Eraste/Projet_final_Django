from rest_framework import viewsets
from blog.serializers import CategorieSerializer,ArticleSerializer,TagSerializer,CommentaireSerializer
from blog.models import Categorie,Article,Tag,Commentaire
from rest_framework.filters import SearchFilter, OrderingFilter

class CommentaireViewSet(viewsets.ModelViewSet):
    
    serializer_class = CommentaireSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['contenu']
    ordering_fields = ['article_id','created_at']

    def get_queryset(self):
        queryset = Commentaire.objects.filter(statut=True)
        auteur = self.request.query_params.get('auteur_id')
        if auteur:
            queryset = queryset.filter(auteur_id=auteur)

        return queryset

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [ 'contenu']
    ordering_fields = ['created_at', 'categorie_id', 'auteur_id']

    def get_queryset(self):
        queryset = Article.objects.filter(est_publie=True, statut=True)
        categorie = self.request.query_params.get('categorie_id')
        auteur = self.request.query_params.get('auteur_id')

        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
        if auteur:
            queryset = queryset.filter(auteur_id=auteur)

        return queryset



class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.filter(statut=True)
    serializer_class = TagSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['created_at']


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.filter(statut=True)
    serializer_class = CategorieSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom','description']
    ordering_fields = ['created_at']
