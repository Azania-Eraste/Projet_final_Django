from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from blog.models import Article,Commentaire
from django.contrib import messages
from Ecommerce.models import VariationProduit,Panier,Favoris, CategorieProduit
from blog.form import InfosGeneralesForm, ContenuForm, StandardsForm, CommentaireForm

# Create your views here.

def index(request):
    panier_produits = None
    favoris_produits = None

    # Récupérer tous les produits actifs (disponibles pour tous)
    produits = VariationProduit.objects.filter(statut=True)

    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        panier_produits = panier.produits.all()

    # Récupérer les catégories actives (disponibles pour tous)
    categories = CategorieProduit.objects.filter(statut=True)

    # Contexte pour le template
    datas = {
        'produits': produits,
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'Categories': categories,
        'active_page': 'accueil'
    }
    
    return render(request, 'index.html', datas)

def contact(request):

    panier_produits = None
    favoris_produits = None



    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        panier_produits = panier.produits.all()

    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        panier_produits = panier.produits.all()

    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        'active_page': 'contact',
        'Categories': categori,
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }

    return render(request, 'contact.html', datas)

def about(request):
    datas = {

    }

    return render(request, 'about.html', datas)

def blog(request):

    articles = Article.objects.filter(est_publie=True, statut=True).order_by("-created_at")
    
    paginator = Paginator(articles, 6) 
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    panier_produits = None
    favoris_produits = None


    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        panier_produits = panier.produits.all()

    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            defaults={'statut': True}
        )
        panier_produits = panier.produits.all()

    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        "articles" : articles,
        "page_obj": page_obj,
        'Categories': categori,
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'active_page': 'blog'
    }

    return render(request, 'blog.html', datas)

def blog_single(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = CommentaireForm()
    datas = {
        "article" : article,
        "form_comment" : form
    }

    if request.method == "POST":
        form = CommentaireForm(request.POST)
        if form.is_valid():
            Commentaire.objects.create(
                article_id=article,
                auteur_id=request.user,
                contenu=form.cleaned_data["contenu"]
            )
            messages.success(request, "Votre commentaire a été ajouté avec succès !")
            return redirect("blog:article", slug=article.slug)

    return render(request, 'blog-single.html', datas)

@login_required(login_url='Authentification:login')
def commentaire_delete(request, slug, id):

    article = get_object_or_404(Article, slug=slug)
    commentaire = get_object_or_404(Commentaire, id=id, article_id=article)

    commentaire.delete()
    messages.success(request, "Commentaire supprimé avec succès.")

    return redirect("blog:article", slug=article.slug)

@login_required(login_url='Authentification:login')
def commentaire_update(request, slug, id):
    article = get_object_or_404(Article, slug=slug)
    commentaire = get_object_or_404(Commentaire, id=id, article_id=article)
    print(commentaire)

    if request.method == 'POST':
        form_comment = CommentaireForm(request.POST, instance=commentaire)
        if form_comment.is_valid():
            form_comment.save()
            messages.success(request, "Commentaire mis à jour avec succès !")
            return redirect('blog:article', slug=article.slug)  # Redirection vers l'article mis à jour
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    else:
        form_comment = CommentaireForm(instance=commentaire)  # Pré-remplir le formulaire avec les données existantes

    return render(request, 'blog-single.html', {
        'form_comment': form_comment,
        'article': article,
        'commentaire': commentaire
    })

def tag_page(request,tag):

    articles = Article.objects.filter(tag=tag)

    paginator = Paginator(articles, 6) 
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    datas = {
        "articles" : articles,
        "page_obj": page_obj
    }

    return render()