from django.contrib import admin
from .models import (
    Role, Produit, CategorieProduit, Commande, Livraison, Mode, Paiement, 
    Panier, Ville, Commune, Adresse, VariationProduit, Avis, CodePromo, Favoris
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("nom",)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "prix", "stock", "categorie")
    search_fields = ("nom",)
    list_filter = ("categorie",)
    ordering = ("nom",)


@admin.register(CategorieProduit)
class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "statut", "utilisateur", "code_promo")
    list_filter = ("statut",)
    search_fields = ("utilisateur__username",)


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ("commande", "transporteur", "statut", "numero_suivi")
    list_filter = ("statut",)
    search_fields = ("numero_suivi",)


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("montant", "mode", "statut")
    list_filter = ("statut",)
    search_fields = ("mode__nom",)


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ("utilisateur",)
    search_fields = ("utilisateur__username",)


@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville")
    search_fields = ("nom", "ville__nom")


@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):
    list_display = ("code_postal", "commune")
    search_fields = ("code_postal", "commune__nom")


@admin.register(VariationProduit)
class VariationProduitAdmin(admin.ModelAdmin):
    list_display = ("produit", "qualite", "poids", "quantite", "prix")
    list_filter = ("qualite", "periode_recolte")
    search_fields = ("produit__nom",)


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "produit", "note", "date")
    list_filter = ("note",)
    search_fields = ("utilisateur__username", "produit__nom")


@admin.register(CodePromo)
class CodePromoAdmin(admin.ModelAdmin):
    list_display = ("code", "reduction", "date_expiration")
    search_fields = ("code",)
    list_filter = ("date_expiration",)


@admin.register(Favoris)
class FavorisAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "produit")
    search_fields = ("utilisateur__username", "produit__nom")
