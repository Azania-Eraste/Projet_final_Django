from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from Authentification.form import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage

# Create your views here.


def login_view(request):


    form = LoginForm()
    error_message = None
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect(reverse('blog:index'))  # Redirige vers la page d'accueil (à modifier selon ton projet)
            else:
                error_message = "Nom d’utilisateur ou mot de passe incorrect."

    datas = {
        'form': form, 
        'message': error_message
    }

    return render(request, 'login.html', datas)

def logout_view(request):
    logout(request)
    return redirect('blog:index')

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirmpassword"]

            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Cet email est déjà utilisé.")
            else:
                # Créer un nouvel utilisateur
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = False
                user.save()

                 # Générer le token et l’uid
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = f"{settings.SITE_URL}/Auth/register/{uid}/{token}/"

                subject = "Activation de votre compte"
                message = f"""
                Bonjour {user.username},

                Merci de vous être inscrit ! Veuillez cliquer sur le lien ci-dessous pour activer votre compte :

                {activation_link}

                Si vous n'avez pas demandé cette inscription, ignorez cet email.

                Merci,
                L'équipe de support.
                """
                email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
                email.send(fail_silently=False)

                messages.success(request, "Un email d'activation vous a été envoyé.")
                return redirect("Authentification:login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def forgetpassword(request):

    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid() : 
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Aucun compte associé à cet email.")
                return render(request, 'forgetpassword.html', {'form': form})
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.SITE_URL}/Auth/forget-password/{uid}/{token}/"

            subject = "Réinitialisation de votre mot de passe"
            message = f"""
            Bonjour {user.username},

            Veuillez cliquer sur le lien ci-dessous pour changer votre mot de passe :

            {reset_link}

            Si vous n'avez pas effectuer cette demande, ignorez cet email.

            Merci,
            L'équipe de support.
            """

            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
            email.send(fail_silently=False)

            messages.success(request, "Un email de réinitialisation a été envoyé.")
            return redirect("Authentification:login")
    else:
        form = ForgetPasswordForm() 

    datas = {
        "form" : form,
    }

    return render(request, 'forgetpassword.html', datas)

def active_account(request,uidb64,token):

    try:
        # Décodage de l'uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect("Authentification:login")
    else:
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")
        return redirect("Authentification:register")

def changepassword(request, uidb64, token):
    try:
        # Décodage de l'uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password"]
                confirm_password = form.cleaned_data["confirmpassword"]

                if password != confirm_password:
                    messages.error(request, "Les mots de passe ne correspondent pas.")
                else:
                    user.set_password(password)  # Hachage du mot de passe
                    user.save()
                    messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
                    return redirect("Authentification:login", {'form': LoginForm()})
        else:
            form = ResetPasswordForm()
        
        return render(request, 'email_reset_password.html', {'form': form})
    
    else:
        messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
        return redirect('Authentification:forgetpassword')
