from django.contrib import admin

from .models import CustomUser, Vendeur


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
