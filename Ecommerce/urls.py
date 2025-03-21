from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard/", views.darshbord, name="board"),
    path("Dashboard/Chechout", views.checkout, name="check"),
    path("Favorite/", views.favorite, name="favorite"),
    path("Shop/", views.shop, name="shop"),
    path("Shop/<int:id>", views.add_dashboard, name="board_add"),
    path("Shop/detail/<int:id>", views.shop_detail, name="detail"),

]