from django.urls import path,include
from Ecommerce import views
from rest_framework.routers import DefaultRouter
from .viewset import (
    ProduitViewSet, CategorieProduitViewSet, CommandeViewSet, CommandeProduitViewSet,
    LivraisonViewSet, ModeViewSet, PaiementViewSet, VilleViewSet, CommuneViewSet,
    AdresseViewSet, PromotionViewSet, VariationProduitViewSet, PanierViewSet,
    AvisViewSet, CodePromoViewSet, FavorisViewSet
)

# Créer un routeur pour les API
router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'categories', CategorieProduitViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'commande-produits', CommandeProduitViewSet)
router.register(r'livraisons', LivraisonViewSet)
router.register(r'modes', ModeViewSet)
router.register(r'paiements', PaiementViewSet)
router.register(r'villes', VilleViewSet)
router.register(r'communes', CommuneViewSet)
router.register(r'adresses', AdresseViewSet)
router.register(r'promotions', PromotionViewSet)
router.register(r'variations', VariationProduitViewSet)
router.register(r'paniers', PanierViewSet)
router.register(r'avis', AvisViewSet)
router.register(r'codes-promo', CodePromoViewSet)
router.register(r'favoris', FavorisViewSet)


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/Profile/", views.profile_view, name="profile"),
    path("Dashboard/Commandes/", views.commandes_view, name="commandes"),
    path('Dashboard/Commandes/<int:commande_id>/', views.commande_detail_view, name='commande_detail'),
    path('Dashboard/Commandes/<int:commande_id>/cancel/', views.commande_cancel_view, name='commande_cancel'),
    path("Dashboard/Paiement/", views.paiement_view, name="mode_paiement"),
    path("Dashboard/Paiement/Remove/<int:mode_id>", views.paiement_remove, name="mode_paiement_remove"),
    path("Panier/", views.panier, name="panier"),
    path('Panier/Confirmation/<int:commande_id>/', views.confirmation, name='confirmation'),
    path("Panier/delete/<slug:slug>/", views.remove_panier, name="panier_remove"),
    path("Panier/add/<slug:slug>/", views.add_panier, name="panier_add"),
    path("Panier/Checkout/", views.checkout, name="check"),
    path("Dashboard/Favorite/", views.favorite, name="favorite"),
    path("Dashboard/Favorite/add/<slug:slug>/", views.add_favorite, name="favorite_add"),
    path("Dashboard/Favorite/delete/<slug:slug>/", views.remove_favorite, name="favorite_remove"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<slug:slug>/", views.shop_detail, name="detail"),
    path("About_us/", views.about_us_view, name="about"),
    path('shipping/', views.shipping_info_view, name='shipping'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('innovation/', views.innovation_view, name='innovation'),
    path('api_Ecommerce/', include(router.urls)),

]