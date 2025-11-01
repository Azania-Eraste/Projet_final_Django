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
    path('register/verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('register/resend-otp/<int:user_id>/', views.resend_otp, name='resend_otp'),
    path('forget-password/', views.forgetpassword, name='forgetpassword'),
    path('devenir-vendeur/', views.devenir_vendeur, name='devenir_vendeur'),
    path('register/<str:uidb64>/<str:token>/', views.active_account, name='activecompte'),
    path('forget-password/<str:uidb64>/<str:token>/', views.changepassword, name='changepassword'),
   
]