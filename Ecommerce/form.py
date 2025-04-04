from django import forms



class CheckForm(forms.Form):
    firstname = forms.CharField(
        widget=forms.TextInput()
    )
    lastname = forms.CharField(
        widget=forms.TextInput()
    )
    ville = forms.CharField(
        widget=forms.TextInput()
    )
    addresse = forms.CharField(
        widget=forms.TextInput()
    )
    commune = forms.CharField(
        widget=forms.TextInput()
    )


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