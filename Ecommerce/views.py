from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Produit, Panier, VariationProduit, CategorieProduit
from django.contrib import messages

# Create your views here.
@login_required(login_url='Authentification:login')
def darshbord(request):  # À renommer en 'dashboard' idéalement
    user = request.user

    # Récupérer ou créer un panier pour l'utilisateur
    panier, created = Panier.objects.get_or_create(
        utilisateur=user,
        defaults={'statut': True}  # Valeurs par défaut si créé
    )

    # Récupérer tous les produits du panier
    produits = panier.produits.all()  # .all() pour obtenir la queryset

    datas = {
        'produits': produits,
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
        return redirect("Ecommerce:board")
    except Produit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")

@login_required(login_url='Authentification:login')
def favorite(request):

    datas = {
        'active_page': 'shop'
    }

    return render(request, 'Favorite.html', datas)

def shop(request):

    produits = VariationProduit.objects.filter(statut=True)
    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        'categories' : categori,
        'produits' : produits,
        'active_page': 'shop'
    }

    return render(request, 'shop-grid.html', datas)

def shop_detail(request, id):

    categori = CategorieProduit.objects.filter(statut=True)
    produit = VariationProduit.objects.get(id=id)

    datas = {
        'active_page': 'shop',
        'categories' : categori,
        'produit' : produit,
    }

    return render(request, 'shop-details.html', datas)