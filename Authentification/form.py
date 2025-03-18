from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nom d’utilisateur'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Mot de passe'})
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Nom d’utilisateur'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Mot de passe'})
    )

    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'email'})
    )
    confirmpassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Comfirmer le mot de passe'})
    )


class ForgetPasswordForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'email'})
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Mot de passe'})
    )
    confirmpassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full h-12 px-4 py-2 text-lg border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Comfirmer le mot de passe'})
    )