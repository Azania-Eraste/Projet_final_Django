from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Commande, Mode, SellerCommande, TypePaiement


@receiver(post_save, sender=User)
def create_default_payment_mode(sender, instance, created, **kwargs):
    if created:
        # Créer un mode de paiement "Liquide" par défaut pour le nouvel utilisateur
        Mode.objects.create(
            utilisateur=instance,
            type_paiement=TypePaiement.LIQUIDE.value,
            statut=True,
            nom="liquide",
        )


@receiver(post_save, sender=Commande)
def notify_vendeurs_on_commande_create(sender, instance, created, **kwargs):
    """Lorsqu'une commande est créée, générer une entrée SellerCommande par vendeur
    et envoyer un email d'alerte à chaque vendeur pour qu'il accepte la commande.
    """
    if not created:
        return

    try:
        # récupérer les vendeurs distincts présents dans la commande
        vendeurs = set()
        for cp in instance.Commande_Produit_ids.select_related(
            "produit", "produit__produit"
        ).all():
            vendeur = (
                cp.produit.produit.vendeur
                if cp.produit and cp.produit.produit
                else None
            )
            if vendeur:
                vendeurs.add(vendeur)

        for vendeur in vendeurs:
            seller_cmd, _ = SellerCommande.objects.get_or_create(
                commande=instance, vendeur=vendeur
            )

            # construire l'url d'acceptation pour le vendeur
            accept_path = reverse(
                "Ecommerce:vendor_accept_seller_commande", args=[seller_cmd.id]
            )
            accept_url = f"{settings.SITE_URL}{accept_path}"

            subject = f"Nouvelle commande #{instance.id} - action requise"
            html = render_to_string(
                "emails/vendor_new_order.html",
                {"vendeur": vendeur, "commande": instance, "accept_url": accept_url},
            )

            email = EmailMessage(
                subject, html, settings.EMAIL_HOST_USER, [vendeur.user.email]
            )
            email.content_subtype = "html"
            try:
                email.send(fail_silently=True)
            except Exception:
                # Ne pas faire échouer la création de commande si l'email ne part pas
                pass
    except Exception:
        # protéger contre erreurs inattendues
        pass
