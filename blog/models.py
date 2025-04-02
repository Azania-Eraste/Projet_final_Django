from django.db import models
from django.contrib.auth import get_user_model
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify


User = get_user_model()

# Create your models here.


class Categorie(models.Model):

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    nom = models.CharField(verbose_name="Nom", max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True,)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)  # Génère un slug basé sur le titre
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom + self.slug
    

class Tag(models.Model):

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    nom = models.CharField(verbose_name="Nom", max_length=255)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom
    

class Article(models.Model):

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    titre = models.CharField(max_length=256)
    couverture = models.ImageField(upload_to="articles")
    resume = models.TextField()
    contenu = CKEditor5Field(config_name='default')
    slug = models.SlugField(unique=True, blank=True,)

    auteur_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="auteur_article_ids", verbose_name="auteurs")
    categorie_id = models.ForeignKey('blog.Categorie', on_delete=models.SET_NULL, null=True, related_name="categorie_article_ids", verbose_name="Catégories")
    tag_ids = models.ManyToManyField('blog.Tag', related_name="tag_article_ids", verbose_name="Tags")
    
    est_publie = models.BooleanField(default=False)
    date_de_publicatio = models.DateField(verbose_name="Date de publication",auto_now=True)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)  # Génère un slug basé sur le titre
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titre
    
    def nombreDeLike(self):
        return self.likes.count()
    

class Commentaire(models.Model):

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    auteur_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="auteur_commentaire_ids")
    article_id = models.ForeignKey('blog.Article', on_delete=models.CASCADE, related_name="article_commentaire_ids")
    contenu = models.TextField()

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.auteur_id.username


class Like(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)  # L'utilisateur qui like
    article = models.ForeignKey('blog.Article', related_name='likes', on_delete=models.CASCADE)  # L'article liké
    date = models.DateTimeField(auto_now_add=True)  # Date du like

    class Meta:
        verbose_name = "like"
        verbose_name_plural = "likes"
        unique_together = ('utilisateur', 'article')  # Un utilisateur ne peut liker qu'une seule fois un article

    def __str__(self):
        return f"{self.utilisateur.username} a liké {self.article.titre}"