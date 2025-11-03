# Projet_final_django — Guide d'installation et scénarios de test

Ce document explique comment préparer l'environnement, lancer le projet Django et réaliser les tests manuels essentiels (commande, confirmation vendeur, devenir livreur, livraisons et code de livraison).

Rédigé pour Windows PowerShell (utilisez `py` ou `python` selon votre installation).

## 1) Prérequis

- Python 3.10/3.11 (ou compatible)
- Git
- Un environnement virtuel (venv, virtualenv)
- Node/npm ou Yarn **non requis** pour l'exécution de base (assets déjà fournis)
- Accès à un serveur SMTP (optionnel) ou utilisez le backend console pour le dev

Ce projet utilise `python-decouple` pour la configuration via `.env`.

## 2) Installer et activer l'environnement

Ouvrez PowerShell dans le dossier racine du dépôt (contenant `projet_final/` et `requirements.txt`).

```powershell
# Créer et activer un venv
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Mettre pip à jour
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

Si l'installation échoue sur des paquets système (p.ex. Pillow), installez les dépendances système requises.

## 3) Fichier de configuration (.env)

Le projet lit certaines variables via `python-decouple`. Créez un fichier `.env` à la racine avec au minimum :

```
SECRET_KEY=changeme_your_secret_key
DEBUG=True
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=yourpassword
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

Notes :
- En développement vous pouvez définir des valeurs factices et/ou utiliser un backend d'email Django `console.EmailBackend` dans `settings.py`.
- Si vous ne souhaitez pas configurer l'email, gardez `DEBUG=True` et les envois d'email sont faits `fail_silently=True` dans le code.

## 4) Initialiser la base de données

```powershell
# Créer les migrations (si nécessaire)
py .\manage.py makemigrations

# Appliquer les migrations
py .\manage.py migrate

# Créer un superuser pour accéder à l'admin
py .\manage.py createsuperuser
```

## 5) Lancer le serveur de développement

```powershell
py .\manage.py runserver
```

Par défaut le site est accessible sur `http://127.0.0.1:8000/`.

## 6) Pages utiles

- Page d'administration : `http://127.0.0.1:8000/admin/`
- Catalogue / shop : `http://127.0.0.1:8000/Shop/`
- Panier : `http://127.0.0.1:8000/Panier/`
- Dashboard vendeur : `http://127.0.0.1:8000/seller/dashboard/`
- Dashboard livreur : `http://127.0.0.1:8000/livreur/dashboard/`
- Pages de gestion de compte (profil, commandes, favoris) sont sous `Dashboard/...` (voir `Ecommerce/urls.py`).

## 7) Scénarios de test manuels (ordre recommandé)

1) Test basique : enregistrer un utilisateur (acheteur)
   - Créez un utilisateur via l'UI ou admin.
   - Connectez-vous, naviguez sur la boutique et ajoutez un produit au panier.

2) Empêcher qu'un vendeur n'achète ses propres produits
   - Créez un compte Vendeur et un produit associé (via admin ou UI `Devenir Vendeur`).
   - Connectez-vous avec ce vendeur et essayez d'ajouter son propre produit au panier. Le système doit bloquer l'ajout/checkout et afficher un message d'erreur.

3) Création de commande (acheteur)
   - Connectez-vous en tant qu'acheteur, ajoutez un produit au panier et procédez au checkout (Panier → Checkout).
   - Vérifiez que la commande est créée avec `statut_commande = En attente` (voir l'admin **Commandes** ou votre page `Dashboard/Commandes/`).

4) Confirmation par le(s) vendeur(s)
   - Les vendeurs concernés (par produit commandé) recevront une `SellerCommande` (voir le dashboard vendeur : `seller/dashboard/`).
   - Le vendeur doit accepter depuis son dashboard (bouton Accepter). Quand tous les vendeurs acceptent, la commande globale passe à `Confirmée`.

5) Devenir livreur
   - En tant qu'utilisateur, soumettez la demande `Devenir Livreur` (page prévue dans l'app Authentification).
   - En admin, approuvez le profil `Livreur` (ou via la page d'administration créée). Une fois approuvé (`active=True`), l'utilisateur peut accéder au dashboard livreur.

6) Flux livraison & code de validation
   - Créez ou suivez une commande avec livraison (via admin ou checkout si livraison est gérée).
   - Accédez au dashboard livreur `livreur/dashboard/`, prenez une livraison (`Prendre`) : le système notifie l'acheteur.
   - Dans le dashboard livreur, cliquez sur `Prendre` puis `Marquer livré` : le livreur ouvre la page d'entrée du code. Lorsqu'un livreur ouvre la page d'entrée du code, le système génère un code (6 chiffres) s'il n'existe pas et l'envoie à l'acheteur par email. L'acheteur verra le code dans son `profile` (champ `livraison_codes` ajouté au contexte).
   - Le livreur saisit le code fourni par le client dans le formulaire; si correct, la livraison est marquée `Livrée` et la commande passe à `Terminee`.

7) Test des emails
   - En dev vous pouvez configurer `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` pour afficher les emails dans la console (utile pour voir les codes générés sans config SMTP).

## 8) Tests automatisés

Si le projet contient des tests unitaires, lancez-les avec :

```powershell
py .\manage.py test
```

Ajoutez des tests pour couvrir :
- Création de commande et statut `En attente`
- Génération et visibilité du code de livraison
- Empêcher l'achat de produits appartenant au vendeur connecté

## 9) Débogage / problèmes fréquents

- Erreur `ModuleNotFoundError: No module named 'decouple'` : installer `python-decouple` (déjà présent dans `requirements.txt`) : `pip install python-decouple`.
- Problèmes d'email : en dev utilisez le backend console ou vérifiez les vars SMTP dans `.env`.
- Si `makemigrations` modifie les modèles (p.ex. champs ajoutés comme `created_at`), exécutez `makemigrations` puis `migrate`.

## 10) Remarques & suggestions

- Les pages principales modifiées pour le flux décrit ci-dessus se trouvent principalement dans :
  - `Ecommerce/views.py`
  - `Ecommerce/models.py`
  - `Ecommerce/templates/` (notamment `livreur/`, `seller/`, `commande_detail.html`, `Favorite.html`)
- Pour automatiser davantage les tests, écrire des tests Django ciblant `Commande`, `SellerCommande` et `Livraison` est recommandé.

---

Si tu veux, je peux :
- Ajouter une petite section du profil utilisateur qui affiche `livraison_codes` (je peux éditer `Ecommerce/Templates/profile.html`).
- Créer un fichier d'exemple `.env.example` avec les clés attendues.
- Écrire quelques tests unitaires pour les scénarios critiques.

Dis-moi ce que tu veux que j'ajoute ensuite.
