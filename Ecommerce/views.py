from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Produit, Panier, StatutCommande, VariationProduit, CategorieProduit, Favoris, Commande, CommandeProduit, Paiement
from django.contrib import messages
from django.core.paginator import Paginator
from Ecommerce.form import PanierQuantiteForm, CheckForm

# Create your views here.

@login_required(login_url='Authentification:login')
def panier(request):
    user = request.user

    panier, created = Panier.objects.get_or_create(
        utilisateur=user,
        defaults={'statut': True}
    )
    produits = panier.produits.all()
    print("Produits dans le panier :", [p.id for p in produits])

    panier_items = []
    if request.method == 'POST':
        if 'passer_commande' in request.POST:
            print("Données POST brutes :", request.POST)
            last_commande = Commande.objects.filter(utilisateur=user).order_by('-id').first()
            print(f"Dernière commande: {last_commande}")
            if not last_commande or last_commande.statut_commande != StatutCommande.EN_ATTENTE:
                commande = Commande(
                    utilisateur=user,
                    statut_commande=StatutCommande.EN_ATTENTE
                )
                form_valid = True
                for produit in produits:
                    prefix = str(produit.id)
                    form = PanierQuantiteForm(request.POST, prefix=prefix)
                    print(f"Produit {produit.id} - Attendu: quantite_{prefix}, produit_id_{prefix}")
                    print(f"Reçu: {request.POST.get(f'quantite_{prefix}')}, {request.POST.get(f'produit_id_{prefix}')}")
                    print(f"Formulaire avant validation: {form.data}")
                    print(f"Est lié (bound) ? {form.is_bound}")
                    if form.is_valid():
                        cleaned_quantite = form.cleaned_data['quantite']
                        cleaned_produit_id = form.cleaned_data['produit_id']
                        if cleaned_produit_id == produit.id:
                            prix_produit = produit.prix_actuel * cleaned_quantite
                            commande_produit = CommandeProduit.objects.create(
                                commande=commande,
                                produit=produit,
                                quantite=cleaned_quantite,
                                prix=prix_produit
                            )
                            
                            print(f"Créé: {commande_produit}")
                        else:
                            print(f"Échec: produit_id mismatch ({cleaned_produit_id} != {produit.id})")
                            form_valid = False
                    else:
                        print(f"Échec: formulaire invalide - Erreurs: {form.errors}")
                        form_valid = False
                commande.save()
                if form_valid:
                    panier.produits.clear()
                    return redirect('Ecommerce:check')
                else:
                    print("Échec global : au moins un formulaire est invalide")
            else:
                messages.warning(request, "Vous avez déjà une commande en attente")
                return redirect('Ecommerce:board')

    for produit in produits:
        initial_data = {
            'quantite': 1,
            'produit_id': produit.id,
        }
        form = PanierQuantiteForm(initial=initial_data, prefix=str(produit.id))
        panier_items.append({'produit': produit, 'form': form})
        print(f"Ajouté à panier_items: produit.id={produit.id}")

    datas = {
        'panier_items': panier_items,
        'Categories': CategorieProduit.objects.filter(statut=True),
        'favoris_produit': Favoris.objects.get_or_create(utilisateur=user, defaults={'statut': True})[0].produit.all(),
        'panier_produit': produits,
        'active_page': 'shop'
    }
    return render(request, 'shoping-cart.html', datas)

@login_required(login_url='Authentification:login')
def checkout(request):
    user = request.user
    print(user)
    form = CheckForm(initial={
        'nom': user.nom,
        'prenom': user.prenom
    })
    print("user.first_name =", user.nom)
    print("user.last_name =", user.prenom)

    # Récupérer la dernière commande
    commande = Commande.objects.filter(utilisateur=user).order_by('-id').first()
    if not commande:
        messages.error(request, "Aucune commande en cours.")
        return redirect("Ecommerce:board")

    # Récupérer les produits de la commande
    produits_commande = commande.Commande_Produit_ids.all()
    print("Produits de la commande :", produits_commande)

    # Récupérer ou créer les favoris et le panier
    favoris, _ = Favoris.objects.get_or_create(utilisateur=user, defaults={'statut': True})
    panier, _ = Panier.objects.get_or_create(utilisateur=user, defaults={'statut': True})

    # Contexte pour le template
    datas = {
        'favoris_produit': favoris.produit.all(),
        'commande': commande,
        'form': form,  
        'produits_commande': produits_commande,
        'panier_produit': panier.produits.all(),
        'total_commande': commande.prix,
        'active_page': 'shop'
    }
    return render(request, 'checkout.html', datas)

@login_required(login_url='Authentification:login')
def add_panier(request, slug):

    datas = {
        'active_page': 'shop'
    }
    
    try:
        produit = VariationProduit.objects.get(slug=slug)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.ajouter_produit(produit)
        messages.success(request, "Produit ajouté au panier")
        return redirect("Ecommerce:board")
    except VariationProduit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


@login_required(login_url='Authentification:login')
def remove_panier(request, slug):

    datas = {
        'active_page': 'shop'
    }

    try:
        produit = VariationProduit.objects.get(slug=slug)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.retirer_produit(produit)
        messages.success(request, "Produit retiré du panier")
        return redirect("Ecommerce:board")
    except VariationProduit.DoesNotExist:
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
def add_favorite(request, slug):

    try:
        produit = VariationProduit.objects.get(slug=slug)
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
def remove_favorite(request, slug):

    try:
        produit = VariationProduit.objects.get(slug=slug)
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
    promo_produit = produits.filter(promotions__active=True).distinct()
    produits = produits.exclude(promotions__active=True).distinct()
    latest_produits = VariationProduit.objects.filter(statut=True).order_by('-created_at')[:6]
    paginator = Paginator(produits, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    view_mode = request.GET.get('view', 'grid')
    print(view_mode)
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
        "page_obj": page_obj,
        "latest_produits":latest_produits,
        'promotion_produit': promo_produit,
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'view_mode': view_mode,
        'active_page': 'shop'
    }

    return render(request, 'shop-grid.html', datas)

def shop_detail(request, slug):

    categori = CategorieProduit.objects.filter(statut=True)
    produit = VariationProduit.objects.get(slug=slug)

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

@login_required(login_url='Authentification:login')
def profile_view(request):

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
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }

    return render(request, 'profile.html', datas)


@login_required(login_url='Authentification:login')
def commandes_view(request):

    commande = Commande.objects.filter(utilisateur=request.user).order_by('-id')


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
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'commandes': commande,
    }

    return render(request, 'commandes.html', datas)


def about_us_view(request):

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
        'active_page': 'about',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }


    return render(request, 'about_us.html', datas)

@login_required(login_url='Authentification:login')
def paiement_view(request):

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

    paiements = Paiement.objects.filter(utilisateur=request.user)

    datas = {
        'active_page': 'shop',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'paiements': paiements
    }

    return render(request, 'paiement.html', datas)