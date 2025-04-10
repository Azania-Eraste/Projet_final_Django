from django import forms
from .models import Mode, TypePaiement, Commune

class CheckForm(forms.Form):
    nom = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    prenom = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    adresse = forms.ModelChoiceField(
        queryset=Commune.objects.none(),  # Sera mis à jour dans la vue
        label="Adresse de livraison",
        empty_label="Sélectionnez une adresse",
        widget=forms.Select(attrs={
            'class': 'form-control my-4',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adresse'].queryset = Commune.objects.filter(statut=True)



class PanierQuantiteForm(forms.Form):
    quantite = forms.IntegerField(min_value=1, required=True)
    produit_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        prefix = self.prefix or ''
        
        # Récupérer les valeurs brutes avec le préfixe
        raw_quantite = self.data.get(f'quantite_{prefix}')
        raw_produit_id = self.data.get(f'produit_id_{prefix}')
        
        # Si les champs ne sont pas dans cleaned_data, les ajouter manuellement
        if raw_quantite and 'quantite' not in cleaned_data:
            try:
                cleaned_data['quantite'] = int(raw_quantite)
                if 'quantite' in self.errors:  # Supprimer l'erreur si elle existe
                    del self.errors['quantite']
            except ValueError:
                self.add_error('quantite', "La quantité doit être un nombre valide.")
        
        if raw_produit_id and 'produit_id' not in cleaned_data:
            try:
                cleaned_data['produit_id'] = int(raw_produit_id)
                if 'produit_id' in self.errors:  # Supprimer l'erreur si elle existe
                    del self.errors['produit_id']
            except ValueError:
                self.add_error('produit_id', "L'ID du produit doit être un nombre valide.")
        
        print(f"Données nettoyées ajustées : {cleaned_data}")
        print(f"Erreurs après ajustement : {self.errors}")
        return cleaned_data
    

class ModePaiementForm(forms.ModelForm):
    class Meta:
        model = Mode
        fields = ['nom', 'description', 'numero_tel', 'numero', 'expiration', 'code']
        widgets = {
            'nom': forms.Select(
                choices=[
                    ('Wave', 'Wave'),
                    ('Orange Money', 'Orange Money'),
                    ('MTN Money', 'MTN Money'),
                    ('Moov Money', 'Moov Money'),
                    ('Carte de crédit/débit', 'Carte de crédit/débit'),
                    ('Carte prépayée', 'Carte prépayée'),
                ],
                attrs={'class': 'form-control mb-3', 'onchange': 'togglePaymentFields()'}
            ),
            'description': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 2}),
            'numero_tel': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ex: +225 01 23 45 67'}),
            'numero': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Numéro de carte'}),
            'expiration': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'MM/AA'}),
            'code': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'CVC ou code'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        numero_tel = cleaned_data.get('numero_tel')
        numero = cleaned_data.get('numero')
        expiration = cleaned_data.get('expiration')
        code = cleaned_data.get('code')

        # Validation conditionnelle avec l’énumération
        if nom in ['Wave', 'Orange Money', 'MTN Money', 'Moov Money']:
            cleaned_data['type_paiement'] = TypePaiement.MOBILE_MONEY.name
            if not numero_tel:
                self.add_error('numero_tel', "Le numéro de téléphone est requis pour ce mode.")
            cleaned_data['numero'] = None
            cleaned_data['expiration'] = None
            cleaned_data['code'] = None
        elif nom == 'Carte de crédit/débit':
            cleaned_data['type_paiement'] = TypePaiement.CREDIT_CARD.name
            if not numero or not expiration or not code:
                self.add_error(None, "Tous les champs de carte sont requis.")
            cleaned_data['numero_tel'] = None
        elif nom == 'Carte prépayée':
            cleaned_data['type_paiement'] = TypePaiement.PREPAID_CARD.name
            if not code:
                self.add_error('code', "Le code de la carte est requis.")
            cleaned_data['numero_tel'] = None
            cleaned_data['numero'] = None
            cleaned_data['expiration'] = None
        return cleaned_data

    def save(self, commit=True, utilisateur=None):
        instance = super().save(commit=False)
        instance.utilisateur = utilisateur
        instance.type_paiement = self.cleaned_data['type_paiement']
        if commit:
            instance.save()
        return instance
