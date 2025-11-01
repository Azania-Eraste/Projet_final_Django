from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def seller_required(view_func):
    """Decorator to ensure the user is an approved seller.

    Redirects to Ecommerce:profile with an error message if not approved.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        if not user or not hasattr(user, 'profil_vendeur') or user.profil_vendeur.statut != 'APPROUVE':
            messages.error(request, "Vous devez être un vendeur approuvé pour accéder à cette page.")
            return redirect('Ecommerce:profile')
        return view_func(request, *args, **kwargs)
    return _wrapped
