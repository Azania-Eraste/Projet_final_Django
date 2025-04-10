from django.db import models
from enum import Enum
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify

User = get_user_model()

class TypePaiement(Enum):
    MOBILE_MONEY = 'Mobile Money'
    CREDIT_CARD = 'Carte de crédit/débit'
    PREPAID_CARD = 'Carte prépayée'

class StatutCommande(Enum):
    EN_ATTENTE = "En attente"
    EN_COURS = "En cours"
    EXPEDIEE = "Expédiée"
    ANNULEE = "Annulée"

class StatutPaiement(Enum):
    EN_ATTENTE = "En attente"
    EFFECTUEE = "Effectué"

class StatutLivraison(Enum):
    EN_COURS = "En cours"
    LIVREE = "Livrée"
    RETOURNEE = "Retournée"

MOIS_CHOICES = [
    (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
    (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
    (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre")
]

class Role(models.Model):
    nom = models.CharField(max_length=255)
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=255)
    Image = models.ImageField(upload_to="Produit")
    description = models.TextField()
    stock = models.IntegerField(default=0)
    categorie = models.ForeignKey('Ecommerce.CategorieProduit', on_delete=models.CASCADE)

    def mettre_a_jour_stock(self):
        nouveau_stock = sum(variation.quantite for variation in self.Variation_Produit_ids.filter(statut=True))
        Produit.objects.filter(pk=self.pk).update(stock=nouveau_stock)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class CategorieProduit(models.Model):
    nom = models.CharField(max_length=255)
    couverture = models.ImageField(upload_to="CategorieProduit")
    slug=models.SlugField(unique=True, blank=True,)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)  # Génère un slug basé sur le titre
        super().save(*args, **kwargs)

    def obtenir_produits(self):
        return Produit.objects.filter(categorie=self)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Commande(models.Model):
    date = models.DateField(auto_now_add=True)
    statut_commande = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in StatutCommande])
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    code_promo = models.ForeignKey('Ecommerce.CodePromo', on_delete=models.SET_NULL, null=True, blank=True)
    paiement = models.OneToOneField('Ecommerce.Paiement', on_delete=models.CASCADE, null=True, blank=True)
    prix = models.FloatField(null=True)
    

    def mettre_a_jour_statut(self, nouveau_statut):
        self.statut_commande = nouveau_statut
        self.save()

    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Commande N" + str(self.pk)
    
class CommandeProduit(models.Model):
    commande = models.ForeignKey('Ecommerce.Commande', on_delete=models.CASCADE, related_name="Commande_Produit_ids")
    produit = models.ForeignKey('Ecommerce.VariationProduit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix = models.FloatField()

    est_actif = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    last_updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ('commande', 'produit')

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} dans commande {self.commande.id}"

class Livraison(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='Livraison_id')
    statut_livraison = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in StatutLivraison])
    adresse = models.ForeignKey('Adresse', on_delete=models.CASCADE, null=True)


    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Livraison N" + str(self.pk)

class Mode(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    nom = models.CharField(max_length=255)  # Ex: "Wave", "Carte de crédit/débit"
    description = models.TextField(blank=True, null=True)
    type_paiement = models.CharField(
        max_length=20,
        choices=[(tag.name, tag.value) for tag in TypePaiement],
        default=TypePaiement.MOBILE_MONEY.name
    )
    numero_tel = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=255, blank=True, null=True)
    expiration = models.CharField(max_length=6, blank=True, null=True)
    code = models.CharField(max_length=6, blank=True, null=True)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} - {self.utilisateur.username}"

    class Meta:
        verbose_name = "Mode de paiement"
        verbose_name_plural = "Modes de paiement"

class Paiement(models.Model):
    montant = models.FloatField()
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mode = models.ForeignKey("Ecommerce.Mode", on_delete=models.CASCADE, related_name="ModePaiement")
    statut_paiement = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in StatutPaiement], null=True)
    est_actif = models.BooleanField(default=True)  # Statut booléen

    def effectuer_paiement(self):
        pass
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Paiement N" + str(self.pk)



class Ville(models.Model):
    nom = models.CharField(max_length=255)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Commune(models.Model):
    nom = models.CharField(max_length=255)
    ville = models.ForeignKey("Ecommerce.Ville", on_delete=models.CASCADE, related_name="Commune_ville_id")

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Adresse(models.Model):
    nom = models.CharField(max_length=255, null=True)
    utilisateur = models.ManyToManyField(User, related_name='Adresse_ids')
    commune = models.ForeignKey("Ecommerce.Commune", on_delete=models.CASCADE, related_name="Adresse_Commune_ids")

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code_postal} {self.commune}"

class Promotion(models.Model):
    nom = models.CharField(max_length=255, help_text="Nom de la promotion, ex: '20% fin de récolte'")
    variations = models.ManyToManyField('Ecommerce.VariationProduit', related_name="promotions", blank=True)
    reduction = models.FloatField(help_text="Réduction en pourcentage (ex: 20 pour 20%)")
    date_debut = models.DateField(help_text="Début de la promotion")
    date_fin = models.DateField(help_text="Fin de la promotion")
    active = models.BooleanField(default=False, help_text="Indique si la promotion est active")
    raison = models.CharField(max_length=255, default="Fin de période de récolte", help_text="Raison de la promotion")

    def est_active(self):
        aujourd_hui = timezone.now().date()
        dans_periode_promo = self.date_debut <= aujourd_hui <= self.date_fin
        return self.active and dans_periode_promo

    def appliquer_reduction(self, prix_initial):
        if self.est_active():
            prix_reduit = prix_initial * (1 - self.reduction / 100)
            return max(prix_reduit, 0)
        return prix_initial

    def appliquer_a_variations(self, variations):
        for variation in variations:
            self.variations.add(variation)

    def retirer_de_variations(self, variations):
        for variation in variations:
            self.variations.remove(variation)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} - {self.reduction}% jusqu'au {self.date_fin}"

class VariationProduit(models.Model):
    nom = models.CharField(max_length=255, null=True)
    produit = models.ForeignKey("Ecommerce.Produit", on_delete=models.CASCADE, related_name="Variation_Produit_ids")
    poids = models.FloatField(help_text="Poids en kilogrammes")
    description = models.TextField(null=True)
    images = models.ImageField(upload_to='Variant_produit', null=True)
    quantite = models.IntegerField(help_text="Quantité disponible")
    origine = models.CharField(max_length=255)
    mois_debut_recolte = models.IntegerField(choices=MOIS_CHOICES, help_text="Mois de début de la période de récolte")
    mois_fin_recolte = models.IntegerField(choices=MOIS_CHOICES, help_text="Mois de fin de la période de récolte")
    prix = models.FloatField(help_text="Prix de la variation du produit")
    qualite = models.CharField(max_length=255, choices=[("Premium", "Premium"), ("Standard", "Standard")])
    slug = models.SlugField( unique=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)  # Génère un slug basé sur le titre
        super().save(*args, **kwargs)


    def est_dans_periode_recolte(self):
        aujourd_hui = timezone.now().date()
        mois_actuel = aujourd_hui.month
        if self.mois_debut_recolte > self.mois_fin_recolte:
            return mois_actuel >= self.mois_debut_recolte or mois_actuel <= self.mois_fin_recolte
        return self.mois_debut_recolte <= mois_actuel <= self.mois_fin_recolte

    def prix_avec_reduction_saison(self):
        if not self.est_dans_periode_recolte():
            prix_reduit = self.prix * (1 - 20 / 100)
            return max(prix_reduit, 0)
        return self.prix

    @property
    def prix_actuel(self):
        prix_base = self.prix_avec_reduction_saison()
        promotions_actives = self.promotions.filter(active=True)
        if promotions_actives.exists():
            promo = promotions_actives.first()
            return promo.appliquer_reduction(prix_base)
        return prix_base

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} - {self.qualite} - {self.poids} kg"
    



class Panier(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Panier_id")
    produits = models.ManyToManyField("Ecommerce.VariationProduit")

    def ajouter_produit(self, produit):
        self.produits.add(produit)

    def retirer_produit(self, produit):
        self.produits.remove(produit)

    def vider_panier(self):
        self.produits.clear()

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Panier N" + str(self.pk)
    

class Avis(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey("Ecommerce.Produit", on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date = models.DateField(auto_now_add=True)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.produit} - {self.note}"

class CodePromo(models.Model):
    code = models.CharField(max_length=50, unique=True)
    reduction = models.FloatField()
    date_expiration = models.DateField()

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Code promo N {self.pk}"

class Favoris(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ManyToManyField("Ecommerce.VariationProduit")

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.utilisateur} aime {self.produit}"

@receiver(post_save, sender=VariationProduit)
@receiver(post_delete, sender=VariationProduit)
def update_produit_stock(sender, instance, **kwargs):
    """Met à jour le stock du produit quand une variation est créée, modifiée ou supprimée."""
    produit = instance.produit
    produit.mettre_a_jour_stock()