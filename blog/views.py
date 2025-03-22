from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from blog.models import Article,Commentaire
from django.contrib import messages
from Ecommerce.models import VariationProduit,Panier,Favoris, CategorieProduit
from blog.form import InfosGeneralesForm, ContenuForm, StandardsForm, CommentaireForm

# Create your views here.

def index(request):

    produit = VariationProduit.objects.filter(statut=True)
    favoris , create = Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
        )


    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        'produits': produit,
        'favoris_produit': favoris.produit,
        'panier_produit': panier.produits,
        'Categories': categori,
        'active_page': 'accueil'
    }

    return render(request, 'index.html', datas)

def contact(request):

    favoris , create= Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
        )
    
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        'active_page': 'contact',
        'Categories': categori,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': panier.produits.all(),
    }

    return render(request, 'contact.html', datas)

@login_required(login_url='Authentification:login')
def darshbord(request):
    user = request.user

    articles = Article.objects.filter(auteur_id=user)


    datas = {
        'articles' : articles
    }

    return render(request, 'dashboard.html', datas)

@login_required(login_url='Authentification:login')
def ajout_article(request):
    if request.method == "POST":
        print("Fichiers reçus :", request.FILES)
        form_infos = InfosGeneralesForm(request.POST, request.FILES)
        form_contenu = ContenuForm(request.POST)
        form_standards = StandardsForm(request.POST)

        print(form_infos.is_valid())
        print(form_contenu.is_valid())
        print(form_standards.is_valid())
         

        if form_infos.is_valid() and form_contenu.is_valid() and form_standards.is_valid():
            # Création de l'article sans sauvegarde immédiate
            print("teste")
            article = Article(
                titre=form_infos.cleaned_data['titre'],
                couverture=request.FILES.get('couverture', None),
                categorie_id=form_infos.cleaned_data['categorie_id'],
                contenu=form_contenu.cleaned_data['contenu'],
                est_publie=form_standards.cleaned_data['est_publie'],
                statut=form_standards.cleaned_data['statut'],
                auteur_id=request.user
            )
            article.save()  # Sauvegarde de l'article

            # Gestion des tags
            article.tag_ids.set(form_infos.cleaned_data['tag_ids'])

            messages.success(request, "Article ajouté avec succès !")
            return redirect('blog:board')

        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    else:
        form_infos = InfosGeneralesForm()
        form_contenu = ContenuForm()
        form_standards = StandardsForm()

    return render(request, 'ajout_article.html', {
        'form_infos': form_infos,
        'form_contenu': form_contenu,
        'form_standards': form_standards
    })

@login_required(login_url='Authentification:login')
def update_article(request, slug):
    # Récupérer l'article existant par son slug
    article = get_object_or_404(Article, slug=slug)

    if request.method == 'POST':
        # Pré-remplir les trois formulaires avec les données existantes de l'article
        form_infos = InfosGeneralesForm(request.POST, request.FILES, instance=article)
        form_contenu = ContenuForm(request.POST, instance=article)
        form_standards = StandardsForm(request.POST, instance=article)

        # Vérifier si tous les formulaires sont valides
        if form_infos.is_valid() and form_contenu.is_valid() and form_standards.is_valid():
            # Sauvegarder les modifications de l'article
            form_infos.save()  # Sauvegarder InfosGeneralesForm
            form_contenu.save()  # Sauvegarder ContenuForm
            form_standards.save()  # Sauvegarder StandardsForm

            # Gestion des tags (si nécessaire)
            article.tag_ids.set(form_infos.cleaned_data['tag_ids'])

            messages.success(request, "Article mis à jour avec succès !")
            return redirect('blog:board')  # Rediriger vers la page des articles
        else:
            messages.error(request, "Veuillez corriger les erreurs dans les formulaires.")
    else:
        # Pré-remplir les formulaires avec les données existantes de l'article lors du GET
        form_infos = InfosGeneralesForm(instance=article)
        form_contenu = ContenuForm(instance=article)
        form_standards = StandardsForm(instance=article)

    return render(request, 'ajout_article.html', {
        'form_infos': form_infos,
        'form_contenu': form_contenu,
        'form_standards': form_standards,
        'article': article,
    })

@login_required(login_url='Authentification:login')
def delete_article(request,slug):

    article = get_object_or_404(Article, slug=slug)
    if article:
        article.statut = False
        article.save()
        return redirect('blog:board')

    return render(request, 'dashboard.html')

def about(request):
    datas = {

    }

    return render(request, 'about.html', datas)

def blog(request):

    articles = Article.objects.filter(est_publie=True, statut=True).order_by("-created_at")
    
    paginator = Paginator(articles, 6) 
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    favoris , create= Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
        )
    
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        "articles" : articles,
        "page_obj": page_obj,
        'Categories': categori,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': panier.produits.all(),
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