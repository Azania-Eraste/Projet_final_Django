from rest_framework import serializers
from .models import (
    Produit, CategorieProduit, Commande, CommandeProduit, Livraison, Mode, Paiement,
    Ville, Commune, Adresse, Promotion, VariationProduit, Panier, Avis, CodePromo, Favoris
)

from blog.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()



# Serializer pour CategorieProduit
class CategorieProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieProduit
        fields = ['id', 'nom', 'couverture', 'slug', 'statut', 'created_at', 'last_updated_at']

# Serializer pour VariationProduit
class VariationProduitSerializer(serializers.ModelSerializer):
    produit = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all())
    prix_actuel = serializers.ReadOnlyField()  # Champ calculé

    class Meta:
        model = VariationProduit
        fields = [
            'id', 'nom', 'produit', 'poids', 'description', 'images', 'quantite', 'origine',
            'mois_debut_recolte', 'mois_fin_recolte', 'prix', 'prix_actuel', 'qualite', 'slug',
            'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Produit
class ProduitSerializer(serializers.ModelSerializer):
    categorie = serializers.PrimaryKeyRelatedField(queryset=CategorieProduit.objects.all())
    Variation_Produit_ids = VariationProduitSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'Image', 'description', 'stock', 'categorie', 'Variation_Produit_ids',
            'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour CommandeProduit
class CommandeProduitSerializer(serializers.ModelSerializer):
    produit = VariationProduitSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=VariationProduit.objects.all(), source='produit', write_only=True
    )

    class Meta:
        model = CommandeProduit
        fields = [
            'id', 'commande', 'produit', 'produit_id', 'quantite', 'prix',
            'est_actif', 'created_at', 'last_updated_at'
        ]

# Serializer pour Mode
class ModeSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', write_only=True
    )

    class Meta:
        model = Mode
        fields = [
            'id', 'utilisateur', 'utilisateur_id', 'nom', 'description', 'type_paiement',
            'numero_tel', 'numero', 'expiration', 'code', 'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Paiement
class PaiementSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', write_only=True
    )
    mode = ModeSerializer(read_only=True)
    mode_id = serializers.PrimaryKeyRelatedField(
        queryset=Mode.objects.all(), source='mode', write_only=True
    )
    commande = serializers.PrimaryKeyRelatedField(queryset=Commande.objects.all())

    class Meta:
        model = Paiement
        fields = [
            'id', 'montant', 'utilisateur', 'utilisateur_id', 'mode', 'mode_id', 'commande',
            'statut_paiement', 'payment_intent_id', 'est_actif', 'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Livraison
class LivraisonSerializer(serializers.ModelSerializer):
    commande = serializers.PrimaryKeyRelatedField(queryset=Commande.objects.all())
    adresse = serializers.PrimaryKeyRelatedField(queryset=Adresse.objects.all())

    class Meta:
        model = Livraison
        fields = [
            'id', 'commande', 'statut_livraison', 'adresse', 'numero_tel', 'frais_livraison',
            'est_actif', 'created_at', 'last_updated_at'
        ]

# Serializer pour Commande
class CommandeSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', write_only=True
    )
    code_promo = serializers.PrimaryKeyRelatedField(queryset=CodePromo.objects.all(), allow_null=True)
    mode = ModeSerializer(read_only=True)
    mode_id = serializers.PrimaryKeyRelatedField(
        queryset=Mode.objects.all(), source='mode', write_only=True, allow_null=True
    )
    Commande_Produit_ids = CommandeProduitSerializer(many=True, read_only=True)
    paiements = PaiementSerializer(many=True, read_only=True)
    Livraison_id = LivraisonSerializer(many=True, read_only=True)

    class Meta:
        model = Commande
        fields = [
            'id', 'date', 'statut_commande', 'utilisateur', 'utilisateur_id', 'code_promo',
            'prix', 'prix_total', 'mode', 'mode_id', 'Commande_Produit_ids', 'paiements',
            'Livraison_id', 'est_actif', 'created_at', 'last_updated_at'
        ]

# Serializer pour Ville
class VilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ville
        fields = ['id', 'nom', 'statut', 'created_at', 'last_updated_at']

# Serializer pour Commune
class CommuneSerializer(serializers.ModelSerializer):
    ville = VilleSerializer(read_only=True)
    ville_id = serializers.PrimaryKeyRelatedField(
        queryset=Ville.objects.all(), source='ville', write_only=True
    )

    class Meta:
        model = Commune
        fields = [
            'id', 'nom', 'ville', 'ville_id', 'frais_livraison',
            'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Adresse
class AdresseSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(many=True, read_only=True)
    utilisateur_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', many=True, write_only=True
    )
    commune = CommuneSerializer(read_only=True)
    commune_id = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(), source='commune', write_only=True
    )

    class Meta:
        model = Adresse
        fields = [
            'id', 'nom', 'utilisateur', 'utilisateur_ids', 'commune', 'commune_id',
            'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Promotion
class PromotionSerializer(serializers.ModelSerializer):
    variations = VariationProduitSerializer(many=True, read_only=True)
    variations_ids = serializers.PrimaryKeyRelatedField(
        queryset=VariationProduit.objects.all(), source='variations', many=True, write_only=True
    )

    class Meta:
        model = Promotion
        fields = [
            'id', 'nom', 'variations', 'variations_ids', 'reduction', 'date_debut', 'date_fin',
            'active', 'raison', 'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Panier
class PanierSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', write_only=True
    )
    produits = VariationProduitSerializer(many=True, read_only=True)
    produits_ids = serializers.PrimaryKeyRelatedField(
        queryset=VariationProduit.objects.all(), source='produits', many=True, write_only=True
    )

    class Meta:
        model = Panier
        fields = [
            'id', 'utilisateur', 'utilisateur_id', 'produits', 'produits_ids',
            'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Avis
class AvisSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', write_only=True
    )
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(), source='produit', write_only=True
    )

    class Meta:
        model = Avis
        fields = [
            'id', 'utilisateur', 'utilisateur_id', 'produit', 'produit_id', 'note',
            'commentaire', 'date', 'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour CodePromo
class CodePromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodePromo
        fields = [
            'id', 'code', 'reduction', 'date_expiration',
            'statut', 'created_at', 'last_updated_at'
        ]

# Serializer pour Favoris
class FavorisSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='utilisateur', write_only=True
    )
    produit = VariationProduitSerializer(many=True, read_only=True)
    produit_ids = serializers.PrimaryKeyRelatedField(
        queryset=VariationProduit.objects.all(), source='produit', many=True, write_only=True
    )

    class Meta:
        model = Favoris
        fields = [
            'id', 'utilisateur', 'utilisateur_id', 'produit', 'produit_ids',
            'statut', 'created_at', 'last_updated_at'
        ]