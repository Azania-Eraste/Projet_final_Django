import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from Authentification.models import Livreur
from Ecommerce.models import Commande, Livraison, StatutCommande, StatutLivraison

User = get_user_model()


class DeliveryQRAndLifecycleTests(TestCase):
    def setUp(self):
        # create buyer
        self.buyer = User.objects.create_user(
            username="buyer", email="buyer@example.com", password="pass"
        )

    def tearDown(self):
        pass

    def test_qr_generation_persists_file(self):
        tmp = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=tmp):
                # create a minimal commande
                commande = Commande.objects.create(
                    utilisateur=self.buyer,
                    prix=0.0,
                    prix_total=0.0,
                    statut_commande=StatutCommande.EN_ATTENTE.value,
                )
                livraison = Livraison.objects.create(
                    commande=commande,
                    statut_livraison=StatutLivraison.EN_ATTENTE.value,
                    delivery_code="999999",
                    numero_tel="000",
                )

                client = Client()
                url = reverse("Ecommerce:livraison_qr_png", args=[livraison.id])
                resp = client.get(url)
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp["Content-Type"], "image/png")

                # file should exist under MEDIA_ROOT/livraison_qr/<id>.png
                expected = os.path.join(tmp, "livraison_qr", f"{livraison.id}.png")
                self.assertTrue(
                    os.path.exists(expected), f"QR file not found at {expected}"
                )
        finally:
            shutil.rmtree(tmp)

    def test_livreur_mark_delivered_flow(self):
        tmp = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=tmp):
                # create commande + livraison
                commande = Commande.objects.create(
                    utilisateur=self.buyer,
                    prix=0.0,
                    prix_total=0.0,
                    statut_commande=StatutCommande.EN_ATTENTE.value,
                )
                livraison = Livraison.objects.create(
                    commande=commande,
                    statut_livraison=StatutLivraison.EN_COURS.value,
                    delivery_code="111111",
                    numero_tel="000",
                )

                # create livreur user and profile
                livreur_user = User.objects.create_user(
                    username="livreur", password="pass"
                )
                Livreur.objects.create(user=livreur_user, active=True, phone="+000")

                client = Client()
                logged = client.login(username="livreur", password="pass")
                self.assertTrue(logged)

                url = reverse("Ecommerce:livreur_mark_delivered", args=[livraison.id])
                resp = client.post(url, {"code": "111111"})
                # should redirect after successful delivery
                self.assertEqual(resp.status_code, 302)

                # refresh from db
                livraison.refresh_from_db()
                commande.refresh_from_db()
                self.assertTrue(livraison.code_used)
                self.assertEqual(
                    commande.statut_commande, StatutCommande.TERMINEE.value
                )
        finally:
            shutil.rmtree(tmp)
