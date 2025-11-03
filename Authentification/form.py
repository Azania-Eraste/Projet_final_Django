from django import forms

from .models import Livreur, Vendeur

FormStyle = """w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none
 focus:ring-2 focus:ring-blue-500"""


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Nom d’utilisateur",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Mot de passe",
            }
        )
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Nom d’utilisateur",
            }
        ),
    )

    nom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Nom",
            }
        )
    )

    prenom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Prenom",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Mot de passe",
            }
        )
    )

    number = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Numero",
            }
        )
    )

    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Email",
            }
        )
    )
    confirmpassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Comfirmer le mot de passe",
            }
        )
    )


class ForgetPasswordForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "class": FormStyle,
                "placeholder": "email",
            }
        )
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Mot de passe",
            }
        )
    )
    confirmpassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": FormStyle,
                "placeholder": "Comfirmer le mot de passe",
            }
        )
    )


class DevenirVendeurForm(forms.ModelForm):
    # Champ supplémentaire pour le numéro, si vous voulez le demander à ce moment
    # Remarque : Ce champ est sur le CustomUser, pas sur Vendeur.
    # Nous le gérerons dans la vue.
    number = forms.CharField(
        label="Votre numéro de téléphone",
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+225 00 00 00 00"}
        ),
    )

    class Meta:
        model = Vendeur
        # Champs du modèle Vendeur que l'utilisateur doit remplir
        fields = ["boutique_name", "boutique_description"]

        widgets = {
            "boutique_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de votre boutique (ex: Le Marché de Yopougon)",
                }
            ),
            "boutique_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Décrivez ce que vous vendez...",
                }
            ),
        }
        labels = {
            "boutique_name": "Nom de la boutique",
            "boutique_description": "Description de la boutique",
        }

    def __init__(self, *args, **kwargs):
        # On récupère l'utilisateur passé depuis la vue
        user = kwargs.pop("user", None)
        super(DevenirVendeurForm, self).__init__(*args, **kwargs)

        # Pré-remplir le champ 'number' avec la valeur du CustomUser
        if user and user.number:
            self.fields["number"].initial = user.number

        # Pré-remplir 'boutique_name' avec le username si le champ est vide
        if user and not self.fields["boutique_name"].initial:
            self.fields["boutique_name"].initial = user.username


class DevenirLivreurForm(forms.ModelForm):
    """Formulaire simple pour qu'un utilisateur demande à devenir livreur."""

    phone = forms.CharField(
        label="Votre numéro de téléphone",
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+225 00 00 00 00"}
        ),
    )

    class Meta:
        model = Livreur
        fields = ["phone"]

        widgets = {
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+225 00 00 00 00"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(DevenirLivreurForm, self).__init__(*args, **kwargs)
        if user and hasattr(user, "number") and user.number:
            self.fields["phone"].initial = user.number


class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "w-full h-12 px-4 py-2 text-lg border rounded-xl",
                "placeholder": "Entrez le code à 6 chiffres",
            }
        ),
    )
