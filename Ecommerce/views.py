from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Max, Min, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from Authentification.decorators import seller_required
from Ecommerce.form import (
    AvisForm,
    CheckForm,
    ModePaiementForm,
    ModePaiementPanierForm,
    PanierQuantiteForm,
)

from .filters import VariationProduitFilter
from .form import ProduitForm, VariationProduitForm
from .models import (
    Adresse,
    Avis,
    CategorieProduit,
    Commande,
    CommandeProduit,
    Favoris,
    Livraison,
    Mode,
    Paiement,
    Panier,
    Produit,
    StatutCommande,
    StatutLivraison,
    StatutPaiement,
    TypePaiement,
    VariationProduit,
)

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()
# Create your views here.


@login_required(login_url="Authentification:login")
def panier(request):
    user = request.user

    panier, created = Panier.objects.get_or_create(
        utilisateur=user, defaults={"statut": True}
    )
    produits = panier.produits.all()
    print("Produits dans le panier :", [p.id for p in produits])

    panier_items = []
    mode_paiement_form = ModePaiementPanierForm(user=user)

    if request.method == "POST":
        if "passer_commande" in request.POST:
            print("Données POST brutes :", request.POST)
            last_commande = (
                Commande.objects.filter(utilisateur=user).order_by("-id").first()
            )
            print(f"Dernière commande: {last_commande}")
            if (
                not last_commande
                or last_commande.statut_commande != StatutCommande.EN_ATTENTE.value
            ):
                mode_paiement_form = ModePaiementPanierForm(request.POST, user=user)
                if mode_paiement_form.is_valid():
                    mode_paiement = mode_paiement_form.cleaned_data["mode_paiement"]
                    commande = Commande(
                        utilisateur=user,
                        statut_commande=StatutCommande.EN_ATTENTE.value,
                        mode=mode_paiement,
                    )
                    commande.save()

                    form_valid = True
                    for produit in produits:
                        prefix = str(produit.id)
                        form = PanierQuantiteForm(request.POST, prefix=prefix)
                        print(
                            f"""
                            Produit {produit.id}
                            Attendu: quantite_{prefix}
                            produit_id_{prefix}
"""
                        )
                        print(
                            f"""
                            Reçu: {request.POST.get(f'quantite_{prefix}')}
                            {request.POST.get(f'produit_id_{prefix}')}
                            """
                        )
                        print(f"Formulaire avant validation: {form.data}")
                        print(f"Est lié (bound) ? {form.is_bound}")
                        if form.is_valid():
                            cleaned_quantite = form.cleaned_data["quantite"]
                            cleaned_produit_id = form.cleaned_data["produit_id"]
                            if cleaned_produit_id == produit.id:
                                prix_actuel = (
                                    produit.prix_actuel()
                                    if callable(produit.prix_actuel)
                                    else produit.prix_actuel
                                )
                                prix_produit = prix_actuel * cleaned_quantite
                                commande_produit = CommandeProduit.objects.create(
                                    commande=commande,
                                    produit=produit,
                                    quantite=cleaned_quantite,
                                    prix=prix_produit,
                                )
                                produit.quantite = produit.quantite - cleaned_quantite
                                print(produit.quantite)
                                produit.save()
                                print(f"Créé: {commande_produit}")
                                print(form_valid)
                            else:
                                print(
                                    f"""
                                    Échec:
                                    produit_id mismatch
                                    ({cleaned_produit_id} != {produit.id})
                                    """
                                )
                                form_valid = False
                        else:
                            print(
                                f"Échec: formulaire invalide - Erreurs: {form.errors}"
                            )
                            form_valid = False

                    if form_valid:
                        commande.prix = sum(
                            produit_commande.prix
                            for produit_commande in commande.Commande_Produit_ids.all()
                        )
                        commande.save()
                        panier.produits.clear()
                        return redirect("Ecommerce:check")
                    else:
                        print(
                            """
                              Échec global :
                            au moins un formulaire est invalide
                              """
                        )
                        commande.delete()
                        messages.error(
                            request,
                            """
                            Erreur lors de la création de la commande.
                            Veuillez vérifier les quantités.
                            """,
                        )
                else:
                    print(
                        "ModePaiementPanierForm invalide - Erreurs:",
                        mode_paiement_form.errors,
                    )
                    messages.error(
                        request, "Veuillez sélectionner un mode de paiement valide."
                    )
            else:
                messages.warning(request, "Vous avez déjà une commande en attente")
                return redirect("Ecommerce:panier")

    for produit in produits:
        initial_data = {
            "quantite": 1,
            "produit_id": produit.id,
        }
        form = PanierQuantiteForm(initial=initial_data, prefix=str(produit.id))
        panier_items.append({"produit": produit, "form": form})
        print(f"Ajouté à panier_items: produit.id={produit.id}")

    datas = {
        "panier_items": panier_items,
        "Categories": CategorieProduit.objects.filter(statut=True),
        "favoris_produit": Favoris.objects.get_or_create(
            utilisateur=user, defaults={"statut": True}
        )[0].produit.all(),
        "panier_produit": produits,
        "active_page": "shop",
        "mode_paiement_form": mode_paiement_form,
    }
    return render(request, "shoping-cart.html", datas)


@login_required(login_url="Authentification:login")
@seller_required
def seller_dashboard(request):
    vendeur = request.user.profil_vendeur
    produits = Produit.objects.filter(vendeur=vendeur)

    # Ventes: somme des prix et nombre de commandes impliquant les produits du vendeur
    ventes_qs = CommandeProduit.objects.filter(
        produit__produit__vendeur=vendeur,
        commande__statut_commande=StatutCommande.CONFIRMEE.value,
    )
    total_revenu = ventes_qs.aggregate(total=Sum("prix"))["total"] or 0
    total_articles_vendus = ventes_qs.aggregate(total_q=Sum("quantite"))["total_q"] or 0

    recent_commandes = (
        Commande.objects.filter(Commande_Produit_ids__produit__produit__vendeur=vendeur)
        .distinct()
        .order_by("-created_at")[:10]
    )

    # Stats par produit (regroupement simple)
    produit_stats = []
    for produit in produits:
        ventes_prod = CommandeProduit.objects.filter(
            produit__produit=produit,
            commande__statut_commande=StatutCommande.CONFIRMEE.value,
        )
        revenu_prod = ventes_prod.aggregate(r=Sum("prix"))["r"] or 0
        quantite_vendue = ventes_prod.aggregate(q=Sum("quantite"))["q"] or 0
        produit_stats.append(
            {
                "produit": produit,
                "revenu": revenu_prod,
                "quantite_vendue": quantite_vendue,
            }
        )

    context = {
        "produits": produits,
        "total_revenu": total_revenu,
        "total_articles_vendus": total_articles_vendus,
        "recent_commandes": recent_commandes,
        "produit_stats": produit_stats,
        "active_page": "seller_dashboard",
    }
    return render(request, "seller/dashboard.html", context)


@login_required(login_url="Authentification:login")
@seller_required
def seller_create_product(request):
    vendeur = request.user.profil_vendeur

    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.vendeur = vendeur
            produit.save()
            messages.success(request, "Produit créé avec succès.")
            return redirect("Ecommerce:seller_dashboard")
    else:
        form = ProduitForm()

    return render(request, "seller/product_form.html", {"form": form})


@login_required(login_url="Authentification:login")
@seller_required
def seller_create_variation(request):
    vendeur = request.user.profil_vendeur

    if request.method == "POST":
        form = VariationProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Variation créée avec succès.")
            return redirect("Ecommerce:seller_dashboard")
    else:
        form = VariationProduitForm()
        form.fields["produit"].queryset = Produit.objects.filter(vendeur=vendeur)

    return render(request, "seller/variation_form.html", {"form": form})


@login_required(login_url="Authentification:login")
def checkout(request):
    user = request.user

    # Initialisation du formulaire
    form = CheckForm(
        initial={
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "phone": user.number,
        }
    )

    # Récupérer la dernière commande
    commande = (
        Commande.objects.filter(
            utilisateur=user, statut_commande=StatutCommande.EN_ATTENTE.value
        )
        .order_by("-id")
        .first()
    )
    if not commande:
        messages.error(request, "Aucune commande en cours.")
        return redirect("Ecommerce:panier")

    # Vérifier que la commande a un mode de paiement
    if not commande.mode:
        messages.error(
            request, "Aucun mode de paiement sélectionné pour cette commande."
        )
        return redirect("Ecommerce:panier")

    # Récupérer les produits de la commande
    produits_commande = commande.Commande_Produit_ids.all()
    print("Produits de la commande :", produits_commande)

    # Récupérer ou créer les favoris et le panier
    favoris, _ = Favoris.objects.get_or_create(
        utilisateur=user, defaults={"statut": True}
    )
    panier, _ = Panier.objects.get_or_create(
        utilisateur=user, defaults={"statut": True}
    )

    # Calcul du sous-total des produits (convertir en Decimal)
    sous_total = Decimal(str(commande.prix))
    frais_livraison = Decimal("0")

    # Vérifier si un paiement a déjà été créé pour cette commande
    paiement = commande.paiements.first()

    if request.method == "POST":
        form = CheckForm(request.POST)
        if form.is_valid():
            commune = form.cleaned_data["adresse"]
            frais_livraison = commune.frais_livraison
            print(f"Frais de livraison : {frais_livraison}")

            # Vérifier si une adresse existe déjà
            adresse_existante = Adresse.objects.filter(
                commune=commune, statut=True
            ).first()
            print(f"{adresse_existante} & {commune.nom}")
            if adresse_existante:
                adresse = adresse_existante
                adresse.utilisateur.add(user)
            else:
                adresse = Adresse.objects.create(
                    nom=f"{commune.nom} - {commune.ville.nom}",
                    commune=commune,
                    statut=True,
                )
                adresse.utilisateur.set([user])

            # Vérifier si une livraison existe déjà pour cette commande
            livraison = Livraison.objects.filter(commande=commande).first()
            if livraison:
                # Si une livraison existe, la mettre à jour
                livraison.adresse = adresse
                livraison.numero_tel = form.cleaned_data["phone"]
                livraison.frais_livraison = frais_livraison
                livraison.statut_livraison = StatutLivraison.EN_COURS.value
                livraison.save()
            else:
                # Sinon, créer une nouvelle livraison
                livraison = Livraison.objects.create(
                    commande=commande,
                    statut_livraison=StatutLivraison.EN_COURS.value,
                    adresse=adresse,
                    numero_tel=form.cleaned_data["phone"],
                    frais_livraison=frais_livraison,
                )

            # Calculer le prix total
            prix_total = Decimal(str(commande.prix)) + frais_livraison
            commande.prix_total = prix_total
            commande.statut_commande = StatutCommande.CONFIRMEE.value
            commande.save()

            # Créer un enregistrement de paiement si ce n'est pas déjà fait
            if not paiement:
                paiement = Paiement.objects.create(
                    montant=float(prix_total),
                    utilisateur=user,
                    mode=commande.mode,
                    commande=commande,
                    statut_paiement=StatutPaiement.EN_ATTENTE.value,
                )
                print(f"Après création : {paiement.statut_paiement}")
                print(f"Avant effectuer_paiement : {paiement.statut_paiement}")
            # Gérer les différents modes de paiement
            if commande.mode.type_paiement == TypePaiement.LIQUIDE.value:
                # Paiement à la livraison
                if paiement.effectuer_paiement():
                    print(f"Après effectuer_paiement : {paiement.statut_paiement}")
                    messages.success(
                        request,
                        "Commande confirmée avec succès (paiement à la livraison).",
                    )
                    return redirect("Ecommerce:confirmation", commande_id=commande.id)

            elif commande.mode.type_paiement == TypePaiement.CREDIT_CARD.value:
                # Paiement via Stripe
                try:
                    payment_intent = stripe.PaymentIntent.create(
                        amount=int(prix_total * 100),
                        currency="xof",
                        payment_method_types=["card"],
                        metadata={
                            "commande_id": commande.id,
                            "paiement_id": paiement.id,
                        },
                        confirm=False,
                    )

                    paiement.payment_intent_id = payment_intent.id
                    paiement.save()
                    print(f"Après effectuer_paiement : {paiement.statut_paiement}")
                    messages.info(
                        request,
                        """
    Veuillez compléter le paiement via Stripe
    pour confirmer votre commande.
                        """,
                    )
                    return redirect("Ecommerce:confirmation", commande_id=commande.id)

                except stripe.error.StripeError as e:
                    messages.error(
                        request,
                        f"""
                        Erreur lors de la création de l'intention de paiement({str(e)})
                        """,
                    )
                    return redirect("Ecommerce:checkout")

            elif commande.mode.type_paiement == TypePaiement.MOBILE_MONEY.value:
                # Simulation d'un paiement Mobile Money
                phone_number = commande.mode.numero_tel
                if not phone_number:
                    messages.error(
                        request,
                        """
                        Numéro de téléphone manquant pour le paiement Mobile Money.
                        """,
                    )
                    return redirect("Ecommerce:checkout")

                # Simuler l'initiation du paiement
                simulated_transaction_id = f"simulated-{commande.id}-{int(prix_total)}"
                paiement.payment_intent_id = simulated_transaction_id
                paiement.save()
                print(f"Après effectuer_paiement : {paiement.statut_paiement}")
                messages.info(
                    request,
                    f"""
                    Simulation :
                    Une demande de paiement a été envoyée à {phone_number}.
                    Veuillez confirmer le paiement sur votre téléphone.
                    """,
                )
                return redirect("Ecommerce:confirmation", commande_id=commande.id)

            elif commande.mode.type_paiement == TypePaiement.PREPAID_CARD.value:
                # Logique pour les cartes prépayées (non implémentée ici)
                messages.error(
                    request,
                    "Le paiement par carte prépayée n'est pas encore pris en charge.",
                )
                return redirect("Ecommerce:checkout")
            else:
                return redirect("Ecommerce:confirmation", commande_id=commande.id)

        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    # Calcul du total avec les frais (pour affichage initial)
    total_avec_frais = sous_total + frais_livraison

    # Contexte pour le template (affichage initial du formulaire)
    datas = {
        "favoris_produit": favoris.produit.all(),
        "commande": commande,
        "form": form,
        "produits_commande": produits_commande,
        "panier_produit": panier.produits.all(),
        "sous_total": sous_total,
        "frais_livraison": frais_livraison,
        "total_avec_frais": total_avec_frais,
        "active_page": "shop",
    }
    return render(request, "checkout.html", datas)


@login_required(login_url="Authentification:login")
def confirmation(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    paiement = commande.paiements.first()

    print(paiement.statut_paiement)

    print(StatutPaiement.EN_ATTENTE.value)

    print(StatutPaiement.EN_ATTENTE.value == paiement.statut_paiement)

    # Vérifier si le paiement a été effectué
    if paiement.statut_paiement == StatutPaiement.EFFECTUE.value:
        commande.statut_commande = StatutCommande.CONFIRMEE.value
        commande.save()
        # Rediriger vers Ecommerce:commandes pour tous les modes sauf CREDIT_CARD
        if commande.mode.type_paiement != TypePaiement.CREDIT_CARD.value:
            messages.success(request, "Commande confirmée avec succès !")
            return redirect("Ecommerce:commandes")

    elif paiement.statut_paiement == StatutPaiement.ECHOUE.value:
        messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
        return redirect("Ecommerce:checkout")

    elif paiement.statut_paiement == StatutPaiement.EN_ATTENTE.value:
        # Générer l'URL de validation pour l'email
        validation_path = reverse("Ecommerce:validate_payment", args=[paiement.id])
        validation_url = f"{settings.SITE_URL}{validation_path}"  # URL complète
        print("ça marche ? 1")
        print(commande.mode.type_paiement)
        print(
            commande.mode.type_paiement
            in [TypePaiement.MOBILE_MONEY.name, TypePaiement.CREDIT_CARD.name]
        )
        # Envoyer un email pour MOBILE_MONEY et CREDIT_CARD
        if commande.mode.type_paiement in [
            TypePaiement.MOBILE_MONEY.name,
            TypePaiement.CREDIT_CARD.name,
        ]:
            # Préparer le contenu de l'email avec le nouveau template Bootstrap
            print("ça marche ? 2")
            subject = "Validation de votre paiement"
            html_message = render_to_string(
                "emails/payment_validation_email_bootstrap.html",
                {
                    "user": request.user,
                    "commande": commande,
                    "validation_url": validation_url,
                },
            )

            # Envoyer l'email
            email_message = EmailMessage(
                subject, html_message, settings.EMAIL_HOST_USER, [request.user.email]
            )
            email_message.content_subtype = "html"
            email_message.send(fail_silently=False)

        if commande.mode.type_paiement == TypePaiement.CREDIT_CARD.value:
            # Vérifier l'état du Payment Intent avec Stripe
            try:
                payment_intent = stripe.PaymentIntent.retrieve(
                    paiement.payment_intent_id
                )
                if payment_intent.status == "succeeded":
                    paiement.statut_paiement = StatutPaiement.EFFECTUE.value
                    commande.statut_commande = StatutCommande.CONFIRMEE.value
                    paiement.save()
                    commande.save()
                else:
                    # Ne pas mettre à jour le statut ici, attendre que
                    # l'utilisateur clique sur le bouton dans l'email
                    pass
            except stripe.error.StripeError as e:
                messages.error(
                    request, f"Erreur lors de la vérification du paiement : {str(e)}"
                )
                return redirect("Ecommerce:checkout")

        elif commande.mode.type_paiement == TypePaiement.MOBILE_MONEY.value:
            # Simulation de la vérification du paiement Mobile Money
            transaction_id = paiement.payment_intent_id
            if transaction_id.startswith("simulated-"):
                # Ne pas confirmer ici, attendre que l'utilisateur
                # clique sur le bouton dans l'email
                pass
            else:
                # Simuler un échec (optionnel)
                paiement.statut_paiement = StatutPaiement.ECHOUE.value
                paiement.save()
                messages.error(
                    request,
                    """
                    Simulation : Le paiement Mobile Money a échoué.
                    Veuillez réessayer.
                    """,
                )
                return redirect("Ecommerce:checkout")

        elif commande.mode.type_paiement in [
            TypePaiement.LIQUIDE.value,
            TypePaiement.PREPAID_CARD.value,
        ]:
            # Pour LIQUIDE et PREPAID_CARD, confirmer directement et rediriger
            paiement.statut_paiement = StatutPaiement.EFFECTUE.value
            commande.statut_commande = StatutCommande.CONFIRMEE.value
            paiement.save()
            commande.save()
            messages.success(request, "Commande confirmée avec succès !")
            return redirect(
                "Ecommerce:commandes"
            )  # Redirection vers Ecommerce:commandes

    # Afficher la page de confirmation uniquement pour CREDIT_CARD et MOBILE_MONEY
    if commande.mode.type_paiement in [
        TypePaiement.CREDIT_CARD.value,
        TypePaiement.MOBILE_MONEY.value,
    ]:
        messages.info(
            request,
            """Un email de validation a été envoyé. Veuillez vérifier
            votre boîte de réception pour confirmer le paiement.""",
        )
        return render(
            request,
            "confirmation.html",
            {
                "commande": commande,
            },
        )
    else:
        # Par sécurité,
        # rediriger vers Ecommerce:commandes si le mode de paiement n'est pas
        # CREDIT_CARD ou MOBILE_MONEY
        return redirect("Ecommerce:commandes")


@login_required(login_url="Authentification:login")
def validate_payment(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id, utilisateur=request.user)
    commande = paiement.commande

    # Vérifier que le paiement est en attente
    if paiement.statut_paiement == StatutPaiement.EN_ATTENTE.value:
        paiement.statut_paiement = StatutPaiement.EFFECTUE.value
        commande.statut_commande = StatutCommande.CONFIRMEE.value
        paiement.save()
        commande.save()
        messages.success(request, "Paiement validé avec succès !")
    else:
        messages.error(
            request, "Le paiement a déjà été traité ou n'est pas en attente."
        )

    return redirect("Ecommerce:commandes")


@login_required(login_url="Authentification:login")
def add_panier(request, slug):
    try:
        produit = VariationProduit.objects.get(slug=slug)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.ajouter_produit(produit)
        messages.success(request, "Produit ajouté au panier")
        return redirect("Ecommerce:panier")
    except VariationProduit.DoesNotExist:
        messages.error(request, "Produit non trouvé")
        return redirect("blog:index")
    except Exception as e:
        print(f"Erreur: {str(e)}")
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


@login_required(login_url="Authentification:login")
def remove_panier(request, slug):
    try:
        produit = VariationProduit.objects.get(slug=slug)
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        panier.retirer_produit(produit)
        messages.success(request, "Produit retiré du panier")
        return redirect("Ecommerce:panier")
    except VariationProduit.DoesNotExist:
        messages.error(request, "Produit non trouvé")
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


@login_required(login_url="Authentification:login")
def favorite(request):
    favoris, create = Favoris.objects.get_or_create(
        utilisateur=request.user, defaults={"statut": True}
    )

    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        defaults={"statut": True},  # Valeurs par défaut si créé
    )

    produits = favoris.produit.all()
    categori = CategorieProduit.objects.filter(statut=True)

    datas = {
        "produits": produits,
        "Categories": categori,
        "favoris_produit": favoris.produit.all(),
        "panier_produit": panier.produits.all(),
        "active_page": "shop",
    }

    return render(request, "Favorite.html", datas)


@login_required(login_url="Authentification:login")
def add_favorite(request, slug):
    try:
        produit = VariationProduit.objects.get(slug=slug)
        favoris, create = Favoris.objects.get_or_create(utilisateur=request.user)
        favoris.produit.add(produit)
        messages.success(request, "Produit ajouté aux favoris")
        return redirect("Ecommerce:favorite")
    except VariationProduit.DoesNotExist:
        messages.error(request, "Produit non trouvé")
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


@login_required(login_url="Authentification:login")
def remove_favorite(request, slug):
    try:
        produit = VariationProduit.objects.get(slug=slug)
        favoris, create = Favoris.objects.get_or_create(utilisateur=request.user)
        favoris.produit.remove(produit)
        messages.success(request, "Produit rétiré des favoris")
        return redirect("Ecommerce:favorite")
    except VariationProduit.DoesNotExist:
        messages.error(request, "Produit non trouvé")
        return redirect("blog:index")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("blog:index")


# Ecommerce/views.py
def shop(request):
    categori = CategorieProduit.objects.filter(statut=True)
    all_produits = VariationProduit.objects.filter(statut=True)
    filter_set = VariationProduitFilter(request.GET, queryset=all_produits)

    # Calculer les valeurs minimales et maximales de prix (approximation initiale)
    promo = (all_produits.aggregate(Min("prix"))["prix__min"] * 50) / 100
    prix_min_global = (all_produits.aggregate(Min("prix"))["prix__min"] - promo) or 0
    prix_max_global = all_produits.aggregate(Max("prix"))["prix__max"] or 1000
    print(promo)
    # Appliquer le filtrage initial (sur prix, nom, categorie)
    promo_produit = filter_set.qs.filter(promotions__active=True).distinct()
    produits = filter_set.qs.exclude(promotions__active=True).distinct()

    # Affiner le filtrage sur prix_actuel
    prix_min = "000"
    prix_min = request.GET.get("prix_min")

    prix_max = request.GET.get("prix_max")

    if prix_min:
        prix_min = prix_min.replace("$", "")
        promo_produit = promo_produit.filter(
            id__in=[p.id for p in promo_produit if p.prix_actuel >= float(prix_min)]
        )
        produits = produits.filter(
            id__in=[p.id for p in produits if p.prix_actuel >= float(prix_min)]
        )
    if prix_max:
        prix_max = prix_max.replace("$", "")
        promo_produit = promo_produit.filter(
            id__in=[p.id for p in promo_produit if p.prix_actuel <= float(prix_max)]
        )
        produits = produits.filter(
            id__in=[p.id for p in produits if p.prix_actuel <= float(prix_max)]
        )
    print(f"=================================={prix_min}-{prix_max}")
    # Appliquer le tri
    sort_by = request.GET.get("sort_by", "default")
    if sort_by == "price_low_to_high":
        produits = produits.order_by("prix")
        promo_produit = promo_produit.order_by("prix")
    elif sort_by == "price_high_to_low":
        produits = produits.order_by("-prix")
        promo_produit = promo_produit.order_by("-prix")

    latest_produits = VariationProduit.objects.filter(statut=True).order_by(
        "-created_at"
    )[:6]
    paginator = Paginator(produits, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    view_mode = request.GET.get("view", "grid")

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

    datas = {
        "Categories": categori,
        "produits": page_obj,
        "page_obj": page_obj,
        "latest_produits": latest_produits,
        "promotion_produit": promo_produit,
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "view_mode": view_mode,
        "active_page": "shop",
        "filter": filter_set,
        "sort_by": sort_by,
        "prix_min_global": int(prix_min_global),
        "prix_max_global": int(prix_max_global),
    }

    return render(request, "shop-grid.html", datas)


def shop_detail(request, slug):
    categori = CategorieProduit.objects.filter(statut=True)
    produit = get_object_or_404(VariationProduit, slug=slug)
    produit_parent = produit.produit
    avis_list = Avis.objects.filter(produit=produit, statut=True).order_by(
        "-created_at"
    )

    has_liked = Favoris.objects.filter(produit=produit, utilisateur=request.user)
    # Calculer la note moyenne
    moyenne_note = avis_list.aggregate(models.Avg("note"))["note__avg"] or 0
    moyenne_note = round(moyenne_note, 1)

    panier_produits = None
    favoris_produits = None
    form_avis = None

    same_produit = (
        VariationProduit.objects.filter(produit=produit_parent, statut=True)
        .exclude(id=produit.id)
        .distinct()[:3]
    )

    if request.user.is_authenticated:
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        favoris_produits = favoris.produit.all()

        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        panier_produits = panier.produits.all()

        if request.method == "POST":
            form_avis = AvisForm(request.POST)
            if form_avis.is_valid():
                avis = form_avis.save(commit=False)
                avis.utilisateur = request.user
                avis.produit = produit
                avis.save()
                messages.success(request, "Votre avis a été ajouté avec succès !")
                return redirect("Ecommerce:detail", slug=slug)
        else:
            form_avis = AvisForm()

    datas = {
        "active_page": "shop",
        "Categories": categori,
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "produit": produit,
        "avis_list": avis_list,
        "form_avis": form_avis,
        "moyenne_note": moyenne_note,
        "same_produit": same_produit,
        "has_liked": has_liked,
    }

    return render(request, "shop-details.html", datas)


@login_required(login_url="Authentification:login")
def profile_view(request):
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

    # 'adresse' result is not used below; remove assignment to avoid lint errors

    datas = {
        "active_page": "shop",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }

    return render(request, "profile.html", datas)


def commandes_view(request):
    panier_produits = None
    favoris_produits = None

    # Récupérer les commandes de l'utilisateur
    commandes = Commande.objects.filter(utilisateur=request.user).order_by("-id")

    if request.user.is_authenticated:
        # Gestion des favoris pour l'utilisateur connecté
        favoris, created = Favoris.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        favoris_produits = favoris.produit.all()

        # Gestion du panier pour l'utilisateur connecté
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user, defaults={"statut": True}
        )
        panier_produits = panier.produits.all()

    datas = {
        "active_page": "shop",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "commandes": commandes,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, "commandes.html", datas)


def about_us_view(request):
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

    datas = {
        "active_page": "about",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }

    return render(request, "about_us.html", datas)


def shipping_info_view(request):
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

    datas = {
        "active_page": "about",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }

    return render(request, "shipping_info.html", datas)


def privacy_policy_view(request):
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

    datas = {
        "active_page": "about",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }

    return render(request, "privacy_policy.html", datas)


def innovation_view(request):
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

    datas = {
        "active_page": "about",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }

    return render(request, "innovation.html", datas)


@login_required(login_url="Authentification:login")
def commande_detail_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    panier_produits = None
    favoris_produits = None
    mode = Mode.objects.filter(utilisateur=request.user)

    livraison, _ = Livraison.objects.get_or_create(commande=commande)
    print(livraison)
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
    print(livraison.statut_livraison)
    paiement = Paiement.objects.filter(utilisateur=request.user, commande=commande)
    print(f"=============================================={paiement}")
    datas = {
        "active_page": "shop",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "commande": commande,
        "livraison": livraison,
        "mode": mode,
        "paiement": paiement,
    }

    return render(request, "commande_detail.html", datas)


@login_required(login_url="Authentification:login")
def commande_cancel_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    if commande.statut_commande != StatutCommande.ANNULEE.value:
        commande.mettre_a_jour_statut(StatutCommande.ANNULEE.value)
        print(commande.statut_commande)
    print(commande.statut_commande)
    return redirect("Ecommerce:commandes")


@login_required(login_url="Authentification:login")
def paiement(request):
    return render(request, "paiement.html", {})


@login_required(login_url="Authentification:login")
def paiement_remove(request, mode_id):
    mode = Mode.objects.get(id=mode_id, utilisateur=request.user)
    mode.statut = False
    mode.save()
    return redirect("Ecommerce:paiement")


@login_required(login_url="Authentification:login")
def paiement_view(request):
    if request.method == "POST":
        form = ModePaiementForm(request.POST)
        if form.is_valid():
            form.save(utilisateur=request.user)
            return redirect("Ecommerce:mode_paiement")
    else:
        form = ModePaiementForm()

    modes = Mode.objects.filter(utilisateur=request.user, statut=True)

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

    datas = {
        "active_page": "shop",
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
        "form": form,
        "modes": modes,
    }

    return render(request, "mode_paiement.html", datas)
