from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/Profile/", views.profile_view, name="profile"),
    path("Dashboard/Commandes/", views.profile_view, name="commandes"),
    path("Dashboard/Paiement/", views.profile_view, name="paiement"),
    path("Panier/", views.panier, name="panier"),
    path("Panier/delete/<slug:slug>", views.remove_panier, name="panier_remove"),
    path("Panier/add/<slug:slug>", views.add_panier, name="panier_add"),
    path("Panier/Chechout", views.checkout, name="check"),
    path("Dashboard/Favorite/", views.favorite, name="favorite"),
    path("Dashboard/Favorite/add/<slug:slug>", views.add_favorite, name="favorite_add"),
    path("Dashboard/Favorite/delete/<slug:slug>", views.remove_favorite, name="favorite_remove"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<slug:slug>", views.shop_detail, name="detail"),
]