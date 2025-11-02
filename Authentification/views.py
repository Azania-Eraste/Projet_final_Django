import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from Authentification.form import (
    ForgetPasswordForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
)
from Ecommerce.models import Favoris, Panier

from .form import DevenirVendeurForm, OTPVerifyForm
from .models import ActivationOTP

# Create your views here.

User = get_user_model()


def login_view(request):
    form = LoginForm()
    error_message = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(
                    reverse("blog:index")
                )  # Redirige vers la page d'accueil (à modifier selon ton projet)
            else:
                error_message = "Nom d’utilisateur ou mot de passe incorrect."

    datas = {"form": form, "message": error_message}

    return render(request, "login.html", datas)


def logout_view(request):
    logout(request)
    return redirect("blog:index")


# Note: register flow replaced by OTP variant below. The original
# activation-link based register_view was removed to avoid duplicate
# definitions. The OTP-based `register_view` remains further down.


def forgetpassword(request):
    if request.method == "POST":
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Aucun compte associé à cet email.")
                return render(request, "forgetpassword.html", {"form": form})

            # Génération du lien de réinitialisation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.SITE_URL}/Auth/forget-password/{uid}/{token}/"

            # Contenu de l'email
            subject = "Réinitialisation de votre mot de passe"
            html_message = render_to_string(
                "emails/reset_password_email.html",
                {
                    "user": user,
                    "reset_link": reset_link,
                },
            )
            plain_message = f"""

            Bonjour {user.username},

            Vous avez demandé à réinitialiser votre mot de passe.
            Pour procéder, veuillez cliquer sur ce lien : {reset_link}

            Si vous n'avez pas effectué cette demande,
            ignorez cet email.\n\nVotre Boutique
            """

            # Envoyer l'email avec une version texte et HTML
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,  # Version texte
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            email_message.attach_alternative(html_message, "text/html")  # Version HTML
            email_message.send(fail_silently=False)

            messages.success(request, "Un email de réinitialisation a été envoyé.")
            return redirect("Authentification:login")
    else:
        form = ForgetPasswordForm()

    return render(request, "forgetpassword.html", {"form": form})


def active_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)  # Correction : User au lieu de user
    except (
        User.DoesNotExist,
        ValueError,
        TypeError,
    ):  # Correction : User au lieu de user
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request,
            """Votre compte a été activé avec succès !
              Vous pouvez maintenant vous connecter.""",
        )
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
                    is_active=False,
                )

                # Générer un OTP numérique de 6 chiffres
                otp_code = "".join(secrets.choice(string.digits) for _ in range(6))
                expires_at = timezone.now() + timedelta(minutes=10)

                # Sauvegarder l'OTP en base
                ActivationOTP.objects.create(
                    user=user, code=otp_code, expires_at=expires_at
                )
                data = {
                    "user": user,
                    "otp_code": otp_code,
                    "expires_minutes": 10,
                }
                # Envoyer le code par email
                subject = "Votre code d'activation"
                html_message = render_to_string(
                    "emails/activation_otp_email.html",
                    data,
                )
                plain_message = f"""
                Bonjour {user.username},

                Votre code d'activation est : {otp_code}
                Il expire dans 10 minutes.

                Si vous n'avez pas demandé cette inscription,
                ignorez cet email.
                """

                email_msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[user.email],
                )
                email_msg.attach_alternative(html_message, "text/html")
                email_msg.send(fail_silently=False)

                messages.success(
                    request, "Un code d'activation a été envoyé à votre email."
                )
                return redirect("Authentification:verify_otp", user_id=user.pk)

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
    except (
        User.DoesNotExist,
        ValueError,
        TypeError,
    ):  # Correction : User au lieu de user
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password"]
                confirm_password = form.cleaned_data["confirmpassword"]

                if password != confirm_password:
                    messages.error(request, "Les mots de passe ne correspondent pas.")
                else:
                    user.set_password(password)
                    user.save()
                    messages.success(
                        request, "Votre mot de passe a été réinitialisé avec succès."
                    )
                    return redirect("Authentification:login")
        else:
            form = ResetPasswordForm()

        return render(request, "email_reset_password.html", {"form": form})

    else:
        messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
        return redirect("Authentification:forgetpassword")


def verify_otp(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("Authentification:register")

    if request.method == "POST":
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].strip()
            otp = (
                ActivationOTP.objects.filter(user=user, used=False)
                .order_by("-created_at")
                .first()
            )
            if not otp:
                messages.error(
                    request, "Aucun code actif trouvé. Demandez un nouveau code."
                )
                return redirect("Authentification:resend_otp", user_id=user.pk)

            if timezone.now() > otp.expires_at:
                messages.error(request, "Le code a expiré. Demandez un nouveau code.")
                return redirect("Authentification:resend_otp", user_id=user.pk)

            if otp.attempts >= 5:
                messages.error(request, "Trop d'essais. Demandez un nouveau code.")
                return redirect("Authentification:resend_otp", user_id=user.pk)

            if code == otp.code:
                otp.used = True
                otp.save()
                user.is_active = True
                user.save()
                messages.success(
                    request,
                    "Votre compte a été activé. Vous pouvez maintenant vous connecter.",
                )
                return redirect("Authentification:login")
            else:
                otp.attempts += 1
                otp.save()
                messages.error(request, "Code invalide. Veuillez réessayer.")
    else:
        form = OTPVerifyForm()

    return render(
        request,
        "otp_verify.html",
        {"form": form, "email": user.email, "user_id": user.pk},
    )


def resend_otp(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("Authentification:register")

    # Rate limit : max 3 OTPs in the last hour
    recent_count = ActivationOTP.objects.filter(
        user=user, created_at__gte=timezone.now() - timedelta(hours=1)
    ).count()
    if recent_count >= 3:
        messages.error(request, "Trop de demandes de code. Réessayez plus tard.")
        return redirect("Authentification:verify_otp", user_id=user.pk)

    otp_code = "".join(secrets.choice(string.digits) for _ in range(6))
    expires_at = timezone.now() + timedelta(minutes=10)
    ActivationOTP.objects.create(user=user, code=otp_code, expires_at=expires_at)
    data = {
        "user": user,
        "otp_code": otp_code,
        "expires_minutes": 10,
    }
    subject = "Votre nouveau code d'activation"
    html_message = render_to_string(
        "emails/activation_otp_email.html",
        data,
    )
    plain_message = f"""
    Bonjour {user.username},
    Votre nouveau code d'activation est : {otp_code}

    Il expire dans 10 minutes.

    Si vous n'avez pas demandé cette inscription, ignorez cet email."""

    email_msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email_msg.attach_alternative(html_message, "text/html")
    email_msg.send(fail_silently=False)

    messages.success(request, "Un nouveau code a été envoyé.")
    return redirect("Authentification:verify_otp", user_id=user.pk)


@login_required  # Garantit que seul un utilisateur connecté peut accéder
def devenir_vendeur(request):
    # Vérifier si l'utilisateur a déjà un profil vendeur
    favoris, created = Favoris.objects.get_or_create(
        utilisateur=request.user, defaults={"statut": True}
    )
    favoris_produits = favoris.produit.all()  # Corrigé : produits au pluriel

    # Gestion du panier pour l'utilisateur connecté
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user, defaults={"statut": True}
    )
    panier_produits = panier.produits.all()

    if hasattr(request.user, "profil_vendeur"):
        profil = request.user.profil_vendeur
        if profil.statut == "APPROUVE":
            messages.info(request, "Vous êtes déjà un vendeur approuvé.")
        elif profil.statut == "EN_ATTENTE":
            messages.info(request, "Votre demande est déjà en cours d'examen.")
        elif profil.statut == "REFUSE":
            messages.error(
                request, "Votre demande précédente a été refusée. Contactez le support."
            )

        return redirect("Ecommerce:profile")  # Rediriger vers son tableau de bord

    # Si la méthode est POST, l'utilisateur a soumis le formulaire
    if request.method == "POST":
        # On passe 'user=request.user' pour la pré-remplissage (si nécessaire)
        form = DevenirVendeurForm(request.POST, user=request.user)

        if form.is_valid():
            # 1. Mettre à jour le CustomUser avec le numéro de téléphone
            user = request.user
            user.number = form.cleaned_data["number"]
            # Si l'utilisateur n'a pas de nom/prénom, on peut les ajouter
            # user.first_name = ... (si vous ajoutez ces champs au formulaire)
            user.save()

            # 2. Créer l'objet Vendeur mais ne pas le sauvegarder en BDD tout de suite
            profil_vendeur = form.save(commit=False)

            # 3. Lier ce nouveau profil à l'utilisateur connecté
            profil_vendeur.user = user

            # 4. Le statut par défaut est déjà 'EN_ATTENTE' (défini dans le modèle)

            # 5. Sauvegarder le nouveau profil Vendeur en BDD
            profil_vendeur.save()

            messages.success(
                request,
                "Votre demande a été envoyée ! Elle est maintenant en cours d'examen.",
            )
            return redirect("Ecommerce:profile")  # Rediriger

    else:
        # Si la méthode est GET, afficher un formulaire vide
        # On passe 'user=request.user' pour pré-remplir le numéro et le nom de boutique
        form = DevenirVendeurForm(user=request.user)

    context = {
        "form": form,
        "active_page": "",  # Pour qu'aucun lien de menu ne soit actif
        "favoris_produit": favoris_produits,
        "panier_produit": panier_produits,
    }
    # Utilise le template HTML que je vous ai montré précédemment
    return render(request, "devenir_vendeur.html", context)
