from django.contrib import admin
from blog.models import Categorie, Tag, Article, Commentaire


class CategorieAdmin(admin.ModelAdmin):

    list_display = ('nom', 'statut', 'created_at', 'last_updated_at', 'slug')

    list_display_links = ['nom',]

    list_filter = ('statut',)

    search_fields = ('nom',)

    date_hierarchy = 'created_at'

    ordering = ['nom',]
    
    list_per_page = 10

    fieldsets = [
            (
                'Infos', 
                {
                    'fields': ['nom', 'description'],
                },
            ),
            (
                'Standards', 
                {
                    'fields': ['statut', ]
                }
            ),
            ]

    actions = ('active','desactive')

    def active(self, request, queryset):
        queryset.update(statut=True)
        self.message_user(request, 'La selection a été activé avec succès')

    active.short_description = 'Activer'

    def desactive(self, request, queryset):
        queryset.update(statut=False)
        self.message_user(request, 'La selection a été désactivé avec succès')

    desactive.short_description = 'Desactiver'


class TagAdmin(admin.ModelAdmin):

    list_display = ['nom','statut', 'created_at', 'last_updated_at']

    list_display_links = ['nom']

    list_filter = ('statut',)

    search_fields = ('nom',)

    date_hierarchy = 'created_at'

    ordering = ['nom',]
    
    list_per_page = 10

    fieldsets = [
            (
                'Infos', 
                {
                    'fields': ['nom',],
                },
            ),
            (
                'Standards', 
                {
                    'fields': ['statut', ]
                }
            ),
            ]

    actions = ('active','desactive')

    def active(self, request, queryset):
        queryset.update(statut=True)
        self.message_user(request, 'La selection a été activé avec succès')

    active.short_description = 'Activer'

    def desactive(self, request, queryset):
        queryset.update(statut=False)
        self.message_user(request, 'La selection a été désactivé avec succès')

    desactive.short_description = 'Desactiver'


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'resume', 'statut', 'slug', 'created_at', 'last_updated_at', 'nombre_likes', 'est_publie']

    list_display_links = ['titre',]

    list_filter = ('statut',)

    search_fields = ('titre',)

    date_hierarchy = 'created_at'

    ordering = ['titre',]
    
    list_per_page = 10

    fieldsets = [
            (
                'Infos', 
                {
                    'fields': ['titre','resume','contenu','couverture','est_publie'],
                },
            ),
            (
                'Organisation', 
                {
                    'fields': ['auteur_id','categorie_id','tag_ids']
                }
            ),
            (
                'Standards', 
                {
                    'fields': ['statut',]
                }
            ),

            ]
    
    readonly_fields = ['nombre_likes']  # Rendre ce champ non modifiable

    def nombre_likes(self, obj):
        return obj.likes.count()  # Compte les likes liés à cet article

    nombre_likes.short_description = "Nombre de Likes"  # Label affiché dans l'admin
    

class CommentaireAdmin(admin.ModelAdmin):

    list_display = ['auteur_id', 'contenu', 'created_at', 'last_updated_at']

    list_display_links = ['auteur_id']

    list_filter = ('statut','article_id')

    date_hierarchy = 'created_at'

    ordering = ['-created_at',]

    list_per_page = 10

    fieldsets = [
            (
                'Infos', 
                {
                    'fields': ['auteur_id','article_id','contenu'],
                },
            ),
            (
                'Standards', 
                {
                    'fields': ['statut',]
                }
            ),
            ]

def _register(model, admin_class):
    admin.site.register(model, admin_class)



_register(Categorie, CategorieAdmin)
_register(Tag, TagAdmin)
_register(Article,ArticleAdmin)
_register(Commentaire,CommentaireAdmin)