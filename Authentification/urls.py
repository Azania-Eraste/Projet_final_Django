from django.urls import path,include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from Authentification import views

app_name = "Authentification"

urlpatterns= [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view,name="logout"),
    path('register/', views.register_view, name='register'),
    path('forget-password/', views.forgetpassword, name='forgetpassword'),
    path('forget-password/<str:uidb64>/<str:token>/', views.changepassword, name='changepassword'),
    path('register/<str:uidb64>/<str:token>/', views.active_account, name='activecompte'),
]