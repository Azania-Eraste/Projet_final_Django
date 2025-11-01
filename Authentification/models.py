from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    nom = models.TextField()
    prenom = models.TextField()
    number = models.TextField()

class Vendeur(models.Model):
    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVE', 'Approuvé'),
        ('REFUSE', 'Refusé'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profil_vendeur' # Ajouté pour un accès facile
    )
    
    boutique_name = models.CharField(max_length=255, blank=True)
    boutique_description = models.TextField(blank=True, null=True)
    
    statut = models.CharField(
        max_length=10, 
        choices=STATUT_CHOICES, 
        default='EN_ATTENTE'  # Le vendeur doit être approuvé
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vendeur"
        verbose_name_plural = "Vendeurs"

    def save(self, *args, **kwargs):
        # Si le nom de la boutique est vide lors de la sauvegarde...
        if not self.boutique_name:
            # ... on assigne le 'username' de l'utilisateur lié.
            self.boutique_name = self.user.username
        super().save(*args, **kwargs) # Appelle la vraie méthode save()

    def __str__(self):
        return self.boutique_name