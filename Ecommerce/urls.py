from django.urls import path,include
from Ecommerce import views


app_name="Ecommerce"

urlpatterns = [
    path("Dashboard", views.darshbord, name="board"),
]