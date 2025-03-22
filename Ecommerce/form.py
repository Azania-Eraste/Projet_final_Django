from django import forms

class PanierQuantiteForm(forms.Form):
    quantite = forms.IntegerField(
        min_value=1,  # Quantité minimale
        initial=1,    # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'qty-input',
            'min': '1',  # Minimum dans le HTML
        })
    )
    produit_id = forms.IntegerField(widget=forms.HiddenInput())  # Champ caché pour identifier le produit