from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model


User = get_user_model()

class StatutCommande(Enum):
    EN_COURS = "En cours"
    EXPEDIEE = "Expédiée"
    ANNULEE = "Annulée"

class StatutLivraison(Enum):
    EN_COURS = "En cours"
    LIVREE = "Livrée"
    RETOURNEE = "Retournée"



class Role(models.Model):
    nom = models.CharField(max_length=255)

class Produit(models.Model):
    nom = models.CharField(max_length=255)
    Image = models.ImageField(upload_to="Produit")
    description = models.TextField()
    prix = models.FloatField()
    stock = models.IntegerField()
    categorie = models.ForeignKey('Ecommerce.CategorieProduit', on_delete=models.CASCADE)

    def mettre_a_jour_stock(self):
        pass

class CategorieProduit(models.Model):
    nom = models.CharField(max_length=255)
    couverture = models.ImageField(upload_to="CategorieProduit")

    def obtenir_produits(self):
        return Produit.objects.filter(categorie=self)
    
    def __str__(self):
        return self.nom

class Commande(models.Model):
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in StatutCommande])
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produits = models.ManyToManyField(Produit)
    code_promo = models.ForeignKey('Ecommerce.CodePromo', on_delete=models.SET_NULL, null=True, blank=True)
    paiement = models.OneToOneField('Ecommerce.Paiement', on_delete=models.CASCADE, null=True, blank=True)

    def mettre_a_jour_statut(self, nouveau_statut):
        self.statut = nouveau_statut
        self.save()

    def __str__(self):
        return  "Commande N" + str(self.pk)

class Livraison(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    transporteur = models.CharField(max_length=255)
    statut = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in StatutLivraison])
    numero_suivi = models.CharField(max_length=255)

    def __str__(self):
        return  "Livraison N" + str(self.pk)
    
class Mode(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.nom

class Paiement(models.Model):
    montant = models.FloatField()
    mode = models.ForeignKey("Ecommerce.Mode", on_delete=models.CASCADE, related_name="ModePaiement")
    statut = models.CharField(max_length=255)

    def effectuer_paiement(self):
        pass

    def __str__(self):
        return "Paiement N" + str(self.pk)


class Panier(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produits = models.ManyToManyField("Ecommerce.Produit")

    def ajouter_produit(self, produit):
        self.produits.add(produit)

    def retirer_produit(self, produit):
        self.produits.remove(produit)

    def vider_panier(self):
        self.produits.clear()

    def __str__(self):
        return "Panier N" + str(self.pk)


class Ville(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Commune(models.Model):
    nom = models.CharField(max_length=255)
    ville = models.ForeignKey("Ecommerce.Ville", on_delete=models.CASCADE, related_name="Commune_ville_ids")
    def __str__(self):
        return self.nom

class Adresse(models.Model):
    code_postal = models.CharField(max_length=10)
    commune = models.ForeignKey("Ecommerce.Commune", on_delete=models.CASCADE, related_name="Adresse_Commune_ids")

    def __str__(self):
        return self.code_postal + self.commune

class VariationProduit(models.Model):
    produit = models.ForeignKey("Ecommerce.Produit", on_delete=models.CASCADE, related_name="Variation_Produit_ids")
    poids = models.FloatField(help_text="Poids en kilogrammes")
    quantite = models.IntegerField(help_text="Quantité disponible (ex: 10 sacs)")
    origine = models.CharField(max_length=255)
    periode_recolte = models.CharField(max_length=255, choices=[("Haute saison", "Haute saison"), ("Basse saison", "Basse saison")])
    prix = models.FloatField(help_text="Prix de la variation du produit")
    qualite = models.CharField(max_length=255, choices=[("Premium", "Premium"), ("Standard", "Standard")])
    
    def __str__(self):
        return f"{self.produit.nom} - {self.qualite} - {self.poids} kg"


class Avis(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey("Ecommerce.Produit", on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.produit} - {self.note}"

class CodePromo(models.Model):
    code = models.CharField(max_length=50, unique=True)
    reduction = models.FloatField()
    date_expiration = models.DateField()

    def __str__(self):
        return f"Code promo N {self.pk}"

class Favoris(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey("Ecommerce.Produit", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.utilisateur} aime {self.produit}"
