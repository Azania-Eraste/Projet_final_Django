from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Authentification.form import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.

User = get_user_model()

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
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        nom = form.cleaned_data["nom"]
        prenom = form.cleaned_data["prenom"]
        email = form.cleaned_data["email"]
        number = form.cleaned_data["number"]
        password = form.cleaned_data["password"]
        confirm_password = form.cleaned_data["confirmpassword"]

        # Vérification des mots de passe
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "register.html", {"form": form})

        # Vérification unicité email et username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, "register.html", {"form": form})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, "register.html", {"form": form})

        try:
            # Création de l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                nom=nom,
                prenom=prenom,
                number=number,
                is_active=False  # Nécessite activation
            )

            # Génération du lien d'activation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"{settings.SITE_URL}/Auth/register/{uid}/{token}/"

            # Contenu de l'email
            subject = "Activation de votre compte"
            html_message = render_to_string('emails/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            plain_message = f"Bonjour {user.username},\n\nMerci de vous être inscrit sur notre site.\nPour activer votre compte, veuillez cliquer sur ce lien : {activation_link}\n\nSi vous n'avez pas demandé cette inscription, ignorez cet email.\n\nVotre Boutique"

            # Envoyer l'email avec une version texte et HTML
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,  # Version texte
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email]
            )
            email_message.attach_alternative(html_message, "text/html")  # Version HTML
            email_message.send(fail_silently=False)

            messages.success(request, "Un email d'activation vous a été envoyé.")
            return redirect("Authentification:login")

        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")

    return render(request, "register.html", {"form": form})


def forgetpassword(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid(): 
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Aucun compte associé à cet email.")
                return render(request, 'forgetpassword.html', {'form': form})
            
            # Génération du lien de réinitialisation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.SITE_URL}/Auth/forget-password/{uid}/{token}/"

            # Contenu de l'email
            subject = "Réinitialisation de votre mot de passe"
            html_message = render_to_string('emails/reset_password_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            plain_message = f"Bonjour {user.username},\n\nVous avez demandé à réinitialiser votre mot de passe.\nPour procéder, veuillez cliquer sur ce lien : {reset_link}\n\nSi vous n'avez pas effectué cette demande, ignorez cet email.\n\nVotre Boutique"

            # Envoyer l'email avec une version texte et HTML
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,  # Version texte
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email]
            )
            email_message.attach_alternative(html_message, "text/html")  # Version HTML
            email_message.send(fail_silently=False)

            messages.success(request, "Un email de réinitialisation a été envoyé.")
            return redirect("Authentification:login")
    else:
        form = ForgetPasswordForm() 

    return render(request, 'forgetpassword.html', {'form': form})


def active_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)  # Correction : User au lieu de user
    except (User.DoesNotExist, ValueError, TypeError):  # Correction : User au lieu de user
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect("Authentification:login")
    else:
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")
        return redirect("Authentification:register")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            nom = form.cleaned_data["nom"]
            prenom = form.cleaned_data["prenom"]
            email = form.cleaned_data["email"]
            number = form.cleaned_data["number"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return render(request, "register.html", {"form": form})

            if User.objects.filter(email=email).exists():
                messages.error(request, "Cet email est déjà utilisé.")
                return render(request, "register.html", {"form": form})

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    nom=nom,
                    prenom=prenom,
                    number=number,
                    is_active=False
                )

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = f"{settings.SITE_URL}/Auth/register/{uid}/{token}/"

                subject = "Activation de votre compte"
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <p style="text-align: center; color: yellow; font-size: 18px; font-weight: bold;">
                        Bonjour {user.username}, merci de vous être inscrit !
                    </p>
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="{activation_link}" 
                           style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; 
                                  border-radius: 5px; display: inline-block;">
                            Activer mon compte
                        </a>
                    </div>
                    <p style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
                        Si vous n'avez pas demandé cette inscription, ignorez cet email.
                    </p>
                </body>
                </html>
                """
                email = EmailMessage(
                    subject,
                    html_message,
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )
                email.content_subtype = "html"  # Indique que le contenu est HTML
                email.send(fail_silently=False)

                messages.success(request, "Un email d'activation vous a été envoyé.")
                return redirect("Authentification:login")

            except Exception as e:
                messages.error(request, f"Une erreur s'est produite : {str(e)}")
                return render(request, "register.html", {"form": form})
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

def changepassword(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)  # Correction : User au lieu de user
    except (User.DoesNotExist, ValueError, TypeError):  # Correction : User au lieu de user
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
                    user.set_password(password)
                    user.save()
                    messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
                    return redirect("Authentification:login")
        else:
            form = ResetPasswordForm()
        
        return render(request, 'email_reset_password.html', {'form': form})
    
    else:
        messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
        return redirect('Authentification:forgetpassword')

