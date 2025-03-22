from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/", views.dashboard, name="board"),
    path("Dashboard/delete/<int:id>", views.remove_dahboard, name="board_remove"),
    path("Dashboard/add/<int:id>", views.add_dashboard, name="board_add"),
    path("Dashboard/Chechout", views.checkout, name="check"),
    path("Favorite/", views.favorite, name="favorite"),
    path("Favorite/add/<int:id>", views.add_favorite, name="favorite_add"),
    path("Favorite/delete/<int:id>", views.remove_favorite, name="favorite_remove"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail/<int:id>", views.shop_detail, name="detail"),
]