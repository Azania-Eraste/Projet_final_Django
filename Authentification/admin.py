from django.contrib import admin
from .models import CustomUser

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username","nom","prenom","number","is_active")
    fieldsets = (
        ("Informations principales", {
            "fields": ("username","password","nom","prenom","number", 'email')
        }),
        ("Métadonnées", {
            "fields": ("is_active",),  # Ajout de la virgule
            "classes": ("collapse",),
        }),
    )