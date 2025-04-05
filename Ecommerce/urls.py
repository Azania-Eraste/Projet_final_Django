from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Panier/", views.dashboard, name="panier"),
    path("Panier/delete/<slug:slug>", views.remove_dahboard, name="panier_remove"),
    path("Panier/add/<slug:slug>", views.add_dashboard, name="panier_add"),
    path("Panier/Chechout", views.checkout, name="check"),
    path("Favorite/", views.favorite, name="favorite"),
    path("Favorite/add/<slug:slug>", views.add_favorite, name="favorite_add"),
    path("Favorite/delete/<slug:slug>", views.remove_favorite, name="favorite_remove"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<slug:slug>", views.shop_detail, name="detail"),
]