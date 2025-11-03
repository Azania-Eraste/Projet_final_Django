from django.contrib import admin

from .models import CustomUser, Livreur, Vendeur


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "nom", "prenom", "number", "is_active")
    fieldsets = (
        (
            "Informations principales",
            {"fields": ("username", "password", "nom", "prenom", "number", "email")},
        ),
        (
            "Métadonnées",
            {
                "fields": ("is_active",),  # Ajout de la virgule
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Vendeur)
class VendeurAdmin(admin.ModelAdmin):
    list_display = ("user", "boutique_name", "statut", "created_at")
    list_filter = ("statut",)
    search_fields = ("user__username", "boutique_name")


@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "active")
    list_filter = ("active",)
    search_fields = ("user__username", "phone")
    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, "Profils livreurs sélectionnés approuvés.")

    def reject_selected(self, request, queryset):
        # supprimer les profils en attente
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} demande(s) refusée(s) et supprimée(s).")

    approve_selected.short_description = "Approuver les livreurs sélectionnés"
    reject_selected.short_description = "Refuser (supprimer) les livreurs sélectionnés"
