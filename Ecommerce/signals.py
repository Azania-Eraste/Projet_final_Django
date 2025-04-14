from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Mode, TypePaiement

@receiver(post_save, sender=User)
def create_default_payment_mode(sender, instance, created, **kwargs):
    if created:
        # Créer un mode de paiement "Liquide" par défaut pour le nouvel utilisateur
        Mode.objects.create(
            utilisateur=instance,
            type_paiement=TypePaiement.LIQUIDE.value,
            statut=True,
            nom = "liquide"
        )