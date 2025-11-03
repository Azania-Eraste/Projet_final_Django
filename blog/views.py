from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from blog.form import CommentaireForm
from blog.models import Article, Categorie, Commentaire, Tag
from Ecommerce.models import CategorieProduit, Favoris, Panier, VariationProduit

from .filters import ArticleFilter

# Create your views here.


def index(request):
    panier_produits = None
    favoris_produits = None
    articles = Article.objects.filter(est_publie=True, statut=True).order_by(
        "-created_at"
    )[:3]

    if request.user.is_authenticated:
        # accéder au profil vendeur sans lever d'exception si absent
        profil_vendeur = getattr(request.user, "profil_vendeur", None)
        if profil_vendeur is not None:
            print(profil_vendeur)
            print(profil_vendeur.statut)
            print(profil_vendeur and profil_vendeur.statut == "APPROUVE")
    # Récupérer tous les produits actifs (disponibles pour tous)
    produits = VariationProduit.objects.filter(statut=True)[:6]

    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        panier_produits = panier.produits.all()

    # Récupérer les catégories actives (disponibles pour tous)
    categories_produit = CategorieProduit.objects.filter(statut=True)

    # Contexte pour le template
    datas = {
        "produits": produits,
        "articles": articles,
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "Categories": categories_produit,
        "active_page": "accueil",
    }

    return render(request, "index.html", datas)


def contact(request):
    panier_produits = None
    favoris_produits = None

    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        panier_produits = panier.produits.all()

    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        "active_page": "contact",
        "Categories": categori,
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }

    return render(request, "contact.html", datas)


def blog(request):
    articles = Article.objects.filter(est_publie=True, statut=True).order_by(
        "-created_at"
    )
    filter_set = ArticleFilter(request.GET, queryset=articles)
    filtered_articles = filter_set.qs

    paginator = Paginator(filtered_articles, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    panier_produits = None
    favoris_produits = None
    if request.user.is_authenticated:
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        favoris_produits = favoris.produit.all()

        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        panier_produits = panier.produits.all()

    categori = CategorieProduit.objects.filter(statut=True)
    categories_article = Categorie.objects.filter(statut=True)
    tag = Tag.objects.filter(statut=True)
    recents = articles[:3]

    datas = {
        "articles": filtered_articles,
        "page_obj": page_obj,
        "filter": filter_set,
        "Categories": categori,
        "Categories_article": categories_article,
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "active_page": "blog",
        "Tags": tag,
        "recents": recents,
    }

    return render(request, "blog.html", datas)


@login_required(login_url="Authentification:login")
def blog_single(request, slug):
    article = get_object_or_404(Article, slug=slug, est_publie=True, statut=True)
    recents = Article.objects.filter(est_publie=True, statut=True).order_by(
        "-created_at"
    )[:3]

    # Articles ayant des tags en commun
    tag_ids = article.tag_ids.values_list("id", flat=True)
    same_tag = (
        Article.objects.filter(tag_ids__in=tag_ids, est_publie=True, statut=True)
        .exclude(id=article.id)
        .distinct()[:3]
    )

    panier_produits = None
    favoris_produits = None
    if request.user.is_authenticated:
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        favoris_produits = favoris.produit.all()

        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        panier_produits = panier.produits.all()

    # Gestion des commentaires
    if request.method == "POST" and request.user.is_authenticated:
        form_comment = CommentaireForm(request.POST)
        if form_comment.is_valid():
            commentaire = form_comment.save(commit=False)
            commentaire.auteur_id = request.user
            commentaire.article_id = article
            commentaire.save()
            messages.success(request, "Votre commentaire a été ajouté avec succès !")
            return redirect("blog:detail", slug=article.slug)
    else:
        form_comment = CommentaireForm()

    context = {
        "article": article,
        "recents": recents,
        "same_tag": same_tag,
        "form_comment": form_comment,
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "active_page": "blog",
    }
    return render(request, "blog-single.html", context)


@login_required(login_url="Authentification:login")
def commentaire_delete(request, slug, id):
    article = get_object_or_404(Article, slug=slug)
    commentaire = get_object_or_404(Commentaire, id=id, article_id=article)

    commentaire.delete()
    messages.success(request, "Commentaire supprimé avec succès.")

    return redirect("blog:detail", slug=article.slug)


@login_required(login_url="Authentification:login")
def commentaire_update(request, slug, id):
    article = get_object_or_404(Article, slug=slug)
    commentaire = get_object_or_404(Commentaire, id=id, article_id=article)
    print(commentaire)

    if request.method == "POST":
        form_comment = CommentaireForm(request.POST, instance=commentaire)
        if form_comment.is_valid():
            form_comment.save()
            messages.success(request, "Commentaire mis à jour avec succès !")
            return redirect(
                "blog:detail", slug=article.slug
            )  # Redirection vers l'article mis à jour
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    else:
        form_comment = CommentaireForm(
            instance=commentaire
        )  # Pré-remplir le formulaire avec les données existantes

    return render(
        request,
        "blog-single.html",
        {"form_comment": form_comment, "article": article, "commentaire": commentaire},
    )


def tag_page(request, tag):
    articles = Article.objects.filter(tag=tag)

    paginator = Paginator(articles, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    datas = {"articles": articles, "page_obj": page_obj}

    return render(request, "blog.html", datas)
