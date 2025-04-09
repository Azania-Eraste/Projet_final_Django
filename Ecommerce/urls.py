from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/Profile/", views.profile_view, name="profile"),
    path("Dashboard/Commandes/", views.commandes_view, name="commandes"),
    path("Dashboard/Paiement/", views.paiement_view, name="paiement"),
    path("Panier/", views.panier, name="panier"),
    path("Panier/delete/<slug:slug>/", views.remove_panier, name="panier_remove"),
    path("Panier/add/<slug:slug>/", views.add_panier, name="panier_add"),
    path("Panier/Chechout/", views.checkout, name="check"),
    path("Dashboard/Favorite/", views.favorite, name="favorite"),
    path("Dashboard/Favorite/add/<slug:slug>/", views.add_favorite, name="favorite_add"),
    path("Dashboard/Favorite/delete/<slug:slug>/", views.remove_favorite, name="favorite_remove"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<slug:slug>/", views.shop_detail, name="detail"),
    path("About_us/", views.about_us_view, name="about"),
    path('shipping/', views.shipping_info_view, name='shipping'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('innovation/', views.innovation_view, name='innovation'),
]