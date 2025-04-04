from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/", views.dashboard, name="board"),
    path("Dashboard/delete/<slug:slug>", views.remove_dahboard, name="board_remove"),
    path("Dashboard/add/<slug:slug>", views.add_dashboard, name="board_add"),
    path("Dashboard/Chechout", views.checkout, name="check"),
    path("Favorite/", views.favorite, name="favorite"),
    path("Favorite/add/<slug:slug>", views.add_favorite, name="favorite_add"),
    path("Favorite/delete/<slug:slug>", views.remove_favorite, name="favorite_remove"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<slug:slug>", views.shop_detail, name="detail"),
]