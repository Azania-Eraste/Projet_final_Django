from rest_framework import viewsets

from .models import (
    Adresse,
    Avis,
    CategorieProduit,
    CodePromo,
    Commande,
    CommandeProduit,
    Commune,
    Favoris,
    Livraison,
    Mode,
    Paiement,
    Panier,
    Produit,
    Promotion,
    VariationProduit,
    Ville,
)
from .serializers import (
    AdresseSerializer,
    AvisSerializer,
    CategorieProduitSerializer,
    CodePromoSerializer,
    CommandeProduitSerializer,
    CommandeSerializer,
    CommuneSerializer,
    FavorisSerializer,
    LivraisonSerializer,
    ModeSerializer,
    PaiementSerializer,
    PanierSerializer,
    ProduitSerializer,
    PromotionSerializer,
    VariationProduitSerializer,
    VilleSerializer,
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
