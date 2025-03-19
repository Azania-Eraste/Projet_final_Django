from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/", views.darshbord, name="board"),
    path("Favorite/", views.favorite, name="favorite"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/detail", views.shop_detail, name="detail"),
]