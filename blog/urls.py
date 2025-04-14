from django.urls import path,include
from blog import views
from django.conf import settings
from django.conf.urls.static import static
from blog.viewsets import ArticleViewSet, CategorieViewSet, TagViewSet, CommentaireViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'categories', CategorieViewSet)
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'tag', TagViewSet)
router.register(r'commentaire', CommentaireViewSet, basename='commentaire')


app_name="blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("Contact/", views.contact, name="contact"),
    path("Blog/<slug:slug>/", views.blog_single, name="detail"),
    path("Blog/<slug:slug>/delete/<int:id>", views.commentaire_delete, name="delete_comment"),
    path("Blog/<slug:slug>/update/<int:id>", views.commentaire_update, name="update_comment"),
    path("Blog/", views.blog, name="blog"),
    path('api_Blog/', include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
