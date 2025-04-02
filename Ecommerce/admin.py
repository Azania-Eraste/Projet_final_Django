from django.contrib import admin
from .models import (
    Role, Produit, CategorieProduit, Commande, Livraison, Mode, Paiement, 
    Panier, Ville, Commune, Adresse, VariationProduit, Avis, CodePromo, Favoris,
    CommandeProduit, Promotion
)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom",)
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom", "variations", "reduction", "date_debut", "date_fin", "active", "raison")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "stock", "categorie")
    search_fields = ("nom",)
    list_filter = ("categorie",)
    ordering = ("nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom", "categorie")
        }),
        ("Détails", {
            "fields": ("Image", "description"),
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(CategorieProduit)
class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ("nom","slug")
    search_fields = ("nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom", "couverture")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "statut_commande", "utilisateur", "code_promo")
    list_filter = ("statut_commande",)
    search_fields = ("utilisateur__username",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("statut_commande", "utilisateur")
        }),
        ("Détails de la commande", {
            "fields": ("code_promo", "paiement"),
        }),
        ("Métadonnées", {
            "fields": ("est_actif",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ("commande", "transporteur", "statut_livraison", "numero_suivi")
    list_filter = ("statut_livraison",)
    search_fields = ("numero_suivi",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("commande", "transporteur", "statut_livraison")
        }),
        ("Suivi", {
            "fields": ("numero_suivi",),  # Déjà correct
        }),
        ("Métadonnées", {
            "fields": ("est_actif",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom", "description")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("montant", "mode", "statut_paiement")
    list_filter = ("statut_paiement",)
    search_fields = ("mode__nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("montant", "mode", "statut_paiement")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ("utilisateur",)
    search_fields = ("utilisateur__username",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("utilisateur", "produits")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom",)
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville")
    search_fields = ("nom", "ville__nom")
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom", "ville")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(CommandeProduit)
class CommandeProduitAdmin(admin.ModelAdmin):
    list_display = ('commande','produit','quantite')
    search_fields = ('produit',)

    fieldsets = (
        ("Informations principales", {
            "fields": ("commande", "produit", "quantite")
        }),
        ("Métadonnées", {
            "fields": ("est_actif",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )


@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):
    list_display = ("code_postal", "commune")
    search_fields = ("code_postal", "commune__nom")
    fieldsets = (
        ("Informations principales", {
            "fields": ("code_postal", "commune")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(VariationProduit)
class VariationProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "produit", "qualite", "poids", "quantite", "prix")
    list_filter = ("qualite", "mois_debut_recolte", "mois_fin_recolte")
    search_fields = ("produit__nom",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom" ,"produit", "images","qualite", "poids", "quantite", "prix")
        }),
        ("Période de récolte", {
            "fields": ("mois_debut_recolte", "mois_fin_recolte", "origine"),
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "produit", "note", "date")
    list_filter = ("note",)
    search_fields = ("utilisateur__username", "produit__nom")
    fieldsets = (
        ("Informations principales", {
            "fields": ("utilisateur", "produit", "note", "commentaire")
        }),
        ("Dates", {
            "fields": ("date",),  # Déjà correct
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(CodePromo)
class CodePromoAdmin(admin.ModelAdmin):
    list_display = ("code", "reduction", "date_expiration")
    search_fields = ("code",)
    list_filter = ("date_expiration",)
    fieldsets = (
        ("Informations principales", {
            "fields": ("code", "reduction", "date_expiration")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )

@admin.register(Favoris)
class FavorisAdmin(admin.ModelAdmin):
    list_display = ("utilisateur",)
    search_fields = ("utilisateur__username", "produit__nom")
    fieldsets = (
        ("Informations principales", {
            "fields": ("utilisateur", "produit")
        }),
        ("Métadonnées", {
            "fields": ("statut",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )