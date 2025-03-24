from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Produit, Panier, StatutCommande, VariationProduit, CategorieProduit, Favoris, Commande, CommandeProduit
from django.contrib import messages
from Ecommerce.form import PanierQuantiteForm

# Create your views here.

@login_required(login_url='Authentification:login')
def dashboard(request):
    user = request.user

    # Gestion des favoris
    favoris, created = Favoris.objects.get_or_create(
        utilisateur=user,
        defaults={'statut': True}
    )

    # Gestion du panier
    panier, created = Panier.objects.get_or_create(
        utilisateur=user,
        defaults={'statut': True}
    )

    # Récupérer les produits du panier
    produits = panier.produits.all()
    categories = CategorieProduit.objects.filter(statut=True)

    # Gestion du formulaire
    panier_items = []
    if request.method == 'POST':
        if 'update_cart' in request.POST:
            # Pas de persistance côté serveur, mise à jour gérée par JS côté client
            return redirect('Ecommerce:dashboard')
        elif 'passer_commande' in request.POST:
            # Créer une nouvelle commande

            last_commande = Commande.objects.all().last()

            if last_commande.statut_commande != StatutCommande.EN_ATTENTE : 
                commande = Commande.objects.create(
                    utilisateur=user,
                    statut_commande=StatutCommande.EN_ATTENTE
                )
                # Ajouter les produits avec leurs quantités à la commande
                for produit in produits:
                    form = PanierQuantiteForm(request.POST, prefix=str(produit.id))
                    if form.is_valid() and form.cleaned_data['produit_id'] == produit.id:
                        CommandeProduit.objects.create(
                            commande=commande,
                            produit=produit,
                            quantite=form.cleaned_data['quantite']
                        )
                # Vider le panier après création de la commande
                panier.produits.clear()
                return redirect('Ecommerce:check')
            else :
                messages.warning(request, "Vous avez deja une commande en attente")
                return redirect('Ecommerce:board')

    # Charger les formulaires avec une quantité initiale de 1
    for produit in produits:
        initial_data = {
            'quantite': 1,
            'produit_id': produit.id,
        }
        form = PanierQuantiteForm(initial=initial_data, prefix=str(produit.id))
        panier_items.append({'produit': produit, 'form': form})

    # Contexte pour le template
    datas = {
        'panier_items': panier_items,
        'Categories': categories,
        'favoris_produit': favoris.produit.all(),
        'panier_produit': produits,
        'active_page': 'shop'
    }

    return render(request, 'shoping-cart.html', datas)

@login_required(login_url='Authentification:login')
def checkout(request):

    user = request.user

    # Gestion des favoris
    favoris, created = Favoris.objects.get_or_create(
        utilisateur=user,
        defaults={'statut': True}
    )

    # Gestion du panier
    panier, created = Panier.objects.get_or_create(
        utilisateur=user,
        defaults={'statut': True}
    )

    datas = {
        'favoris_produit': favoris.produit.all() ,  # Gestion ForeignKey vs ManyToMany
        'panier_produit': panier.produits.all(),
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
    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        'produits' : produits,
        'Categories': categori,
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

    datas = {
        'Categories': categori,
        'produits' : produits,
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'active_page': 'shop'
    }

    return render(request, 'shop-grid.html', datas)

def shop_detail(request, id):

    categori = CategorieProduit.objects.filter(statut=True)
    produit = VariationProduit.objects.get(id=id)

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

    

    datas = {
        'active_page': 'shop',
        'Categories': categori,
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'produit' : produit,
    }

    return render(request, 'shop-details.html', datas)