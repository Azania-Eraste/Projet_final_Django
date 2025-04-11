from rest_framework import serializers
from blog.models import Categorie,Article,Tag,Commentaire
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
      class Meta: 
            model = User
            fields = [
                        'id',
                        'username',
                        'email',
                        'nom',
                        'prenom',
                        'number',
                    ]
            
            
            
class TagSerializer(serializers.ModelSerializer):
        class Meta:
            model = Tag
            fields = ['id','nom',]

class CommentaireSerializer(serializers.ModelSerializer):
        class Meta:
            model = Commentaire
            fields = [
                        'id',
                        'auteur_id',
                        'article_id',
                        'contenu',
                    ]
            
class CategorieIdSerializer(serializers.ModelSerializer):

        class Meta:
            model = Categorie
            fields = ['id','nom','description',]

class ArticleSerializer(serializers.ModelSerializer):
        
        auteur_id = UserSerializer()
        tag_ids = TagSerializer(many=True)
        categorie_id = CategorieIdSerializer()

        class Meta:
            depth = 1
            model = Article
            fields = [  
                        'id',
                        'titre',
                        'couverture',
                        'resume',
                        'contenu',
                        'auteur_id',
                        'categorie_id',
                        'tag_ids',
                        'date_de_publicatio',
                    ]


class CategorieSerializer(serializers.ModelSerializer):
        
        categorie_article_ids = ArticleSerializer(many=True)

        class Meta:
            model = Categorie
            fields = ['id','nom','description', 'categorie_article_ids']

