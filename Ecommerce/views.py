from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import (
    Produit, Panier, StatutCommande, VariationProduit, CategorieProduit, Favoris, 
    Commande, CommandeProduit, Paiement, Adresse, Mode, Livraison, Avis, StatutLivraison, StatutPaiement
    )
from django.contrib import messages
from django.core.paginator import Paginator
from Ecommerce.form import PanierQuantiteForm, CheckForm, ModePaiementForm, ModePaiementPanierForm
from django.contrib.auth import get_user_model
from decimal import Decimal


User = get_user_model()
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
    mode_paiement_form = ModePaiementPanierForm(user=user)

    if request.method == 'POST':
        if 'passer_commande' in request.POST:
            print("Données POST brutes :", request.POST)
            last_commande = Commande.objects.filter(utilisateur=user).order_by('-id').first()
            print(f"Dernière commande: {last_commande}")
            if not last_commande or last_commande.statut_commande != StatutCommande.EN_ATTENTE.value:
                mode_paiement_form = ModePaiementPanierForm(request.POST, user=user)
                if mode_paiement_form.is_valid():
                    mode_paiement = mode_paiement_form.cleaned_data['mode_paiement']
                    commande = Commande(
                        utilisateur=user,
                        statut_commande=StatutCommande.EN_ATTENTE.value,
                        mode=mode_paiement
                    )
                    commande.save()

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
                                prix_actuel = produit.prix_actuel() if callable(produit.prix_actuel) else produit.prix_actuel
                                prix_produit = prix_actuel * cleaned_quantite
                                commande_produit = CommandeProduit.objects.create(
                                    commande=commande,
                                    produit=produit,
                                    quantite=cleaned_quantite,
                                    prix=prix_produit
                                )
                                print(f"Créé: {commande_produit}")
                                print(form_valid)
                            else:
                                print(f"Échec: produit_id mismatch ({cleaned_produit_id} != {produit.id})")
                                form_valid = False
                        else:
                            print(f"Échec: formulaire invalide - Erreurs: {form.errors}")
                            form_valid = False

                    if form_valid:
                        commande.prix = sum(
                            produit_commande.prix 
                            for produit_commande in commande.Commande_Produit_ids.all()
                        )
                        commande.save()
                        panier.produits.clear()
                        return redirect('Ecommerce:check')
                    else:
                        print("Échec global : au moins un formulaire est invalide")
                        commande.delete()
                        messages.error(request, "Erreur lors de la création de la commande. Veuillez vérifier les quantités.")
                else:
                    print("ModePaiementPanierForm invalide - Erreurs:", mode_paiement_form.errors)
                    messages.error(request, "Veuillez sélectionner un mode de paiement valide.")
            else:
                messages.warning(request, "Vous avez déjà une commande en attente")
                return redirect('Ecommerce:panier')

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
        'active_page': 'shop',
        'mode_paiement_form': mode_paiement_form,
    }
    return render(request, 'shoping-cart.html', datas)



@login_required(login_url='Authentification:login')
def checkout(request):
    user = request.user  # Instance de CustomUser

    # Initialisation du formulaire
    form = CheckForm(initial={
        'nom': user.nom,
        'prenom': user.prenom,
        'email': user.email,
        'phone': user.number,
    })

    # Récupérer la dernière commande
    commande = Commande.objects.filter(utilisateur=user,statut_commande=StatutCommande.EN_ATTENTE.value).order_by('-id').first()
    if not commande:
        messages.error(request, "Aucune commande en cours.")
        return redirect("Ecommerce:panier")

    # Récupérer les produits de la commande
    produits_commande = commande.Commande_Produit_ids.all()
    print("Produits de la commande :", produits_commande)

    # Récupérer ou créer les favoris et le panier
    favoris, _ = Favoris.objects.get_or_create(utilisateur=user, defaults={'statut': True})
    panier, _ = Panier.objects.get_or_create(utilisateur=user, defaults={'statut': True})

    # Calcul du sous-total des produits (convertir en Decimal)
    sous_total = Decimal(str(commande.prix))  # Convertir float en Decimal
    frais_livraison = Decimal('0')  # Initialisé en Decimal

    if request.method == 'POST':
        form = CheckForm(request.POST)
        if form.is_valid():
            commune = form.cleaned_data['adresse']  # Instance de Commune
            frais_livraison = commune.frais_livraison  # Déjà un Decimal
            print(f"Frais de livraison : {frais_livraison}")

            # Vérifier si une adresse existe déjà
            adresse_existante = Adresse.objects.filter(
                utilisateur=user,
                commune=commune,
                statut=True
            ).first()

            if adresse_existante:
                adresse = adresse_existante
            else:
                adresse = Adresse.objects.create(
                    nom=f"{commune.nom} {commune.ville.nom}",
                    commune=commune,
                    statut=True
                )
                adresse.utilisateur.set([user])

            # Créer la livraison avec les frais en FCFA
            livraison = Livraison.objects.create(
                commande=commande,
                statut_livraison=StatutLivraison.EN_COURS.value,
                adresse=adresse,
                numero_tel=form.cleaned_data['phone'],
                frais_livraison=frais_livraison
            )

            # Calculer et enregistrer le prix total
            commande.prix_total = Decimal(str(commande.prix)) + frais_livraison
            commande.statut_commande = StatutCommande.CONFIRMEE.value
            commande.save()  # Sauvegarder la mise à jour dans la base

            messages.success(request, "Commande passée avec succès !")
            return redirect("Ecommerce:commandes")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    # Rendre certains champs en lecture seule
    form.fields['nom'].widget.attrs['readonly'] = 'readonly'
    form.fields['prenom'].widget.attrs['readonly'] = 'readonly'
    form.fields['email'].widget.attrs['readonly'] = 'readonly'

    # Calcul du total avec les frais (pour affichage initial)
    total_avec_frais = sous_total + frais_livraison

    # Contexte pour le template
    datas = {
        'favoris_produit': favoris.produit.all(),
        'commande': commande,
        'form': form,
        'produits_commande': produits_commande,
        'panier_produit': panier.produits.all(),
        'sous_total': sous_total,
        'frais_livraison': frais_livraison,  # Ajout pour affichage si nécessaire
        'total_avec_frais': total_avec_frais,
        'active_page': 'shop'
    }
    return render(request, 'checkout.html', datas)



@login_required(login_url='Authentification:login')
def add_panier(request, slug):

    
    try:
        produit = VariationProduit.objects.get(slug=slug)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.ajouter_produit(produit)
        messages.success(request, "Produit ajouté au panier")
        return redirect("Ecommerce:panier")
    except VariationProduit.DoesNotExist:
        messages.error(request, 'Produit non trouvé')
        return redirect("blog:index")
    except Exception as e:
        print(f"Erreur: {str(e)}")
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


@login_required(login_url='Authentification:login')
def remove_panier(request, slug):


    try:
        produit = VariationProduit.objects.get(slug=slug)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.retirer_produit(produit)
        messages.success(request, "Produit retiré du panier")
        return redirect("Ecommerce:panier")
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

    adresse = Adresse.objects.filter(utilisateur=request.user)

    datas = {
        'active_page': 'shop',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }

    return render(request, 'profile.html', datas)


@login_required(login_url='Authentification:login')
def commandes_view(request):

    panier_produits = None
    favoris_produits = None

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
        'active_page': 'about',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }


    return render(request, 'about_us.html', datas)

def shipping_info_view(request):

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
        'active_page': 'about',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }

    return render(request, 'shipping_info.html', datas)

def privacy_policy_view(request):

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
        'active_page': 'about',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }

    return render(request, 'privacy_policy.html', datas)


def innovation_view(request):

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
        'active_page': 'about',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
    }

    return render(request, 'innovation.html', datas)

@login_required(login_url='Authentification:login')
def commande_detail_view(request, commande_id):

    commande = get_object_or_404(Commande, id=commande_id)
    panier_produits = None
    favoris_produits = None
    mode = Mode.objects.filter(utilisateur=request.user)

    livraison,_= Livraison.objects.get_or_create(commande=commande)
    print(livraison)
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
        print(livraison.statut_livraison)
    datas = {
        'active_page': 'about',
        'favoris_produit': favoris_produits,
        'panier_produit': panier_produits,
        'commande': commande,
        'livraison': livraison,
        'mode': mode,
    }

    return render(request, 'commande_detail.html', datas)

@login_required(login_url='Authentification:login')
def commande_cancel_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    if commande.statut_commande != StatutCommande.ANNULEE.value:
        commande.mettre_a_jour_statut(StatutCommande.ANNULEE.value)
        print(commande.statut_commande)
    print(commande.statut_commande)
    return redirect('Ecommerce:commandes')



@login_required(login_url='Authentification:login')
def paiement(request):

    return render(request, 'paiement.html', {

    })

@login_required(login_url='Authentification:login')
def paiement_remove(request, mode_id):
    mode = Mode.objects.get(id=mode_id, utilisateur=request.user)
    mode.statut = False
    mode.save()
    return redirect('Ecommerce:paiement')

@login_required(login_url='Authentification:login')
def paiement_view(request):

    if request.method == 'POST':
        form = ModePaiementForm(request.POST)
        if form.is_valid():
            form.save(utilisateur=request.user)
            return redirect('Ecommerce:mode_paiement')
    else:
        form = ModePaiementForm()

    modes = Mode.objects.filter(utilisateur=request.user, statut=True)


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
        'form': form,
        'modes': modes,
    }

    return render(request, 'mode_paiement.html', datas)


