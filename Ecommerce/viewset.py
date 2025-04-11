from rest_framework import viewsets
from .models import (
    Produit, CategorieProduit, Commande, CommandeProduit, Livraison, Mode, Paiement,
    Ville, Commune, Adresse, Promotion, VariationProduit, Panier, Avis, CodePromo, Favoris
)
from .serializers import (
    ProduitSerializer, CategorieProduitSerializer, CommandeSerializer, CommandeProduitSerializer,
    LivraisonSerializer, ModeSerializer, PaiementSerializer, VilleSerializer, CommuneSerializer,
    AdresseSerializer, PromotionSerializer, VariationProduitSerializer, PanierSerializer,
    AvisSerializer, CodePromoSerializer, FavorisSerializer
)

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class CategorieProduitViewSet(viewsets.ModelViewSet):
    queryset = CategorieProduit.objects.all()
    serializer_class = CategorieProduitSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

class CommandeProduitViewSet(viewsets.ModelViewSet):
    queryset = CommandeProduit.objects.all()
    serializer_class = CommandeProduitSerializer

class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonSerializer

class ModeViewSet(viewsets.ModelViewSet):
    queryset = Mode.objects.all()
    serializer_class = ModeSerializer

class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

class VilleViewSet(viewsets.ModelViewSet):
    queryset = Ville.objects.all()
    serializer_class = VilleSerializer

class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer

class AdresseViewSet(viewsets.ModelViewSet):
    queryset = Adresse.objects.all()
    serializer_class = AdresseSerializer

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

class VariationProduitViewSet(viewsets.ModelViewSet):
    queryset = VariationProduit.objects.all()
    serializer_class = VariationProduitSerializer

class PanierViewSet(viewsets.ModelViewSet):
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer

class AvisViewSet(viewsets.ModelViewSet):
    queryset = Avis.objects.all()
    serializer_class = AvisSerializer

class CodePromoViewSet(viewsets.ModelViewSet):
    queryset = CodePromo.objects.all()
    serializer_class = CodePromoSerializer

class FavorisViewSet(viewsets.ModelViewSet):
    queryset = Favoris.objects.all()
    serializer_class = FavorisSerializer