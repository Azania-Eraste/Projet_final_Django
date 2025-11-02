from django.urls import include, path
from rest_framework.routers import DefaultRouter

from Ecommerce import views

from .viewset import (
    AdresseViewSet,
    AvisViewSet,
    CategorieProduitViewSet,
    CodePromoViewSet,
    CommandeProduitViewSet,
    CommandeViewSet,
    CommuneViewSet,
    FavorisViewSet,
    LivraisonViewSet,
    ModeViewSet,
    PaiementViewSet,
    PanierViewSet,
    ProduitViewSet,
    PromotionViewSet,
    VariationProduitViewSet,
    VilleViewSet,
)

# Créer un routeur pour les API
router = DefaultRouter()
router.register(r"produits", ProduitViewSet)
router.register(r"categories", CategorieProduitViewSet)
router.register(r"commandes", CommandeViewSet)
router.register(r"commande-produits", CommandeProduitViewSet)
router.register(r"livraisons", LivraisonViewSet)
router.register(r"modes", ModeViewSet)
router.register(r"paiements", PaiementViewSet)
router.register(r"villes", VilleViewSet)
router.register(r"communes", CommuneViewSet)
router.register(r"adresses", AdresseViewSet)
router.register(r"promotions", PromotionViewSet)
router.register(r"variations", VariationProduitViewSet)
router.register(r"paniers", PanierViewSet)
router.register(r"avis", AvisViewSet)
router.register(r"codes-promo", CodePromoViewSet)
router.register(r"favoris", FavorisViewSet)


app_name = "Ecommerce"

urlpatterns = [
    path("Dashboard/Profile/", views.profile_view, name="profile"),
    path("Dashboard/Commandes/", views.commandes_view, name="commandes"),
    path(
        "Dashboard/Commandes/<int:commande_id>/",
        views.commande_detail_view,
        name="commande_detail",
    ),
    path(
        "Dashboard/Commandes/<int:commande_id>/cancel/",
        views.commande_cancel_view,
        name="commande_cancel",
    ),
    path("Dashboard/Paiement/", views.paiement_view, name="mode_paiement"),
    path(
        "Dashboard/Paiement/<int:paiement_id>",
        views.validate_payment,
        name="validate_payment",
    ),
    path(
        "Dashboard/Paiement/Remove/<int:mode_id>",
        views.paiement_remove,
        name="mode_paiement_remove",
    ),
    path("Panier/", views.panier, name="panier"),
    path(
        "Panier/Confirmation/<int:commande_id>/",
        views.confirmation,
        name="confirmation",
    ),
    path("Panier/delete/<slug:slug>/", views.remove_panier, name="panier_remove"),
    path("Panier/add/<slug:slug>/", views.add_panier, name="panier_add"),
    path("Panier/Checkout/", views.checkout, name="check"),
    path("Dashboard/Favorite/", views.favorite, name="favorite"),
    path(
        "Dashboard/Favorite/add/<slug:slug>/", views.add_favorite, name="favorite_add"
    ),
    path(
        "Dashboard/Favorite/delete/<slug:slug>/",
        views.remove_favorite,
        name="favorite_remove",
    ),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<slug:slug>/", views.shop_detail, name="detail"),
    path("About_us/", views.about_us_view, name="about"),
    path("shipping/", views.shipping_info_view, name="shipping"),
    path("privacy/", views.privacy_policy_view, name="privacy"),
    path("innovation/", views.innovation_view, name="innovation"),
    path("api_Ecommerce/", include(router.urls)),
    # Seller routes
    path("seller/dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path(
        "seller/product/create/",
        views.seller_create_product,
        name="seller_create_product",
    ),
    path(
        "seller/variation/create/",
        views.seller_create_variation,
        name="seller_create_variation",
    ),
    # route pour accepter/refuser une commande par vendeur
    path(
        "seller/order/<int:seller_commande_id>/accept/",
        views.vendor_accept_seller_commande,
        name="vendor_accept_seller_commande",
    ),
]
