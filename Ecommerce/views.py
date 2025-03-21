from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Produit, Panier, VariationProduit, CategorieProduit, Favoris
from django.contrib import messages

# Create your views here.
@login_required(login_url='Authentification:login')
def darshbord(request):  # À renommer en 'dashboard' idéalement
    user = request.user

    favoris , create = Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
        )


    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    # Récupérer tous les produits du panier
    produits = panier.produits.all()  # .all() pour obtenir la queryset

    datas = {
        'produits': produits,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': panier.produits.all(),
        'active_page': 'shop'
    }

    return render(request, 'shoping-cart.html', datas)


@login_required(login_url='Authentification:login')
def checkout(request):

    datas = {
        'active_page': 'shop'
    }
    return render(request, 'checkout.html', datas)


@login_required(login_url='Authentification:login')
def add_dashboard(request, id):

    datas = {
        'active_page': 'shop'
    }
    
    try:
        produit = VariationProduit.objects.get(id=id)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.ajouter_produit(produit)
        messages.success(request, "Produit ajouté au panier")
        return redirect("Ecommerce:board")
    except Produit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


@login_required(login_url='Authentification:login')
def remove_dahboard(request, id):

    datas = {
        'active_page': 'shop'
    }

    try:
        produit = VariationProduit.objects.get(id=id)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.retirer_produit(produit)
        messages.success(request, "Produit retiré du panier")
        return redirect("Ecommerce:board")
    except Produit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")

@login_required(login_url='Authentification:login')
def favorite(request):

    favoris , create= Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
        )
    
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )
    
    produits = favoris.produit.all()

    datas = {
        'produits' : produits,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': panier.produits.all(),
        'active_page': 'shop'
    }

    return render(request, 'Favorite.html', datas)

@login_required(login_url='Authentification:login')
def add_favorite(request, id):

    try:
        produit = VariationProduit.objects.get(id=id)
        favoris , create = Favoris.objects.get_or_create(utilisateur=request.user)
        favoris.produit.add(produit)
        messages.success(request, "Produit ajouté aux favoris")
        return redirect("Ecommerce:favorite")
    except VariationProduit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")
    
@login_required(login_url='Authentification:login')
def remove_favorite(request, id):

    try:
        produit = VariationProduit.objects.get(id=id)
        favoris , create = Favoris.objects.get_or_create(utilisateur=request.user)
        favoris.produit.remove(produit)
        messages.success(request, "Produit rétiré des favoris")
        return redirect("Ecommerce:favorite")
    except VariationProduit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")

def shop(request):

    produits = VariationProduit.objects.filter(statut=True)
    categori = CategorieProduit.objects.filter(statut=True)

    favoris , create= Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
    )
    
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    datas = {
        'categories' : categori,
        'produits' : produits,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': panier.produits.all(),
        'active_page': 'shop'
    }

    return render(request, 'shop-grid.html', datas)

def shop_detail(request, id):

    categori = CategorieProduit.objects.filter(statut=True)
    produit = VariationProduit.objects.get(id=id)

    favoris , create= Favoris.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}
        )
    
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    datas = {
        'active_page': 'shop',
        'categories' : categori,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': panier.produits.all(),
        'produit' : produit,
    }

    return render(request, 'shop-details.html', datas)