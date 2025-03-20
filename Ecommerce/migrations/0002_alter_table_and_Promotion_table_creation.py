from django.db import migrations, models
from django.utils import timezone

# Définir MOIS_CHOICES directement dans la migration
MOIS_CHOICES = [
    (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
    (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
    (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre")
]

class Migration(migrations.Migration):
    dependencies = [
        ('Ecommerce', '0001_initial'),  # Assurez-vous que ceci correspond à votre migration précédente
    ]

    operations = [
        # Renommage des champs statut
        migrations.RenameField(
            model_name='commande',
            old_name='statut',
            new_name='statut_commande',
        ),
        migrations.RenameField(
            model_name='livraison',
            old_name='statut',
            new_name='statut_livraison',
        ),

        # Création du modèle Promotion (si non présent dans 0001_initial)
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255, help_text="Nom de la promotion, ex: '20% fin de récolte'")),
                ('reduction', models.FloatField(help_text="Réduction en pourcentage (ex: 20 pour 20%)")),
                ('date_debut', models.DateField(help_text="Début de la promotion")),
                ('date_fin', models.DateField(help_text="Fin de la promotion")),
                ('active', models.BooleanField(default=True, help_text="Indique si la promotion est active")),
                ('raison', models.CharField(max_length=255, default="Fin de période de récolte", help_text="Raison de la promotion")),
                ('variations', models.ManyToManyField(blank=True, related_name='promotions', to='Ecommerce.VariationProduit')),
            ],
            options={
                'verbose_name': 'Promotion',
                'verbose_name_plural': 'Promotions',
            },
        ),

        # Ajout des champs standards à tous les modèles
        # Role
        migrations.AddField(
            model_name='role',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='role',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Produit
        migrations.AddField(
            model_name='produit',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='produit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='produit',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # CategorieProduit
        migrations.AddField(
            model_name='categorieproduit',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='categorieproduit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='categorieproduit',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Commande
        migrations.AddField(
            model_name='commande',
            name='est_actif',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commande',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Livraison
        migrations.AddField(
            model_name='livraison',
            name='est_actif',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='livraison',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='livraison',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Mode
        migrations.AddField(
            model_name='mode',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mode',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Paiement
        migrations.AddField(
            model_name='paiement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paiement',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Panier
        migrations.AddField(
            model_name='panier',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='panier',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='panier',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Ville
        migrations.AddField(
            model_name='ville',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='ville',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ville',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Commune
        migrations.AddField(
            model_name='commune',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='commune',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commune',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Adresse
        migrations.AddField(
            model_name='adresse',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='adresse',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='adresse',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Promotion (ajout des champs standards)
        migrations.AddField(
            model_name='promotion',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='promotion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='promotion',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # VariationProduit (suppression de periode_recolte et ajout des nouveaux champs)
        migrations.RemoveField(
            model_name='variationproduit',
            name='periode_recolte',
        ),
        migrations.AddField(
            model_name='variationproduit',
            name='mois_debut_recolte',
            field=models.IntegerField(choices=MOIS_CHOICES, help_text="Mois de début de la période de récolte"),
        ),
        migrations.AddField(
            model_name='variationproduit',
            name='mois_fin_recolte',
            field=models.IntegerField(choices=MOIS_CHOICES, help_text="Mois de fin de la période de récolte"),
        ),
        migrations.AddField(
            model_name='variationproduit',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='variationproduit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='variationproduit',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Avis
        migrations.AddField(
            model_name='avis',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='avis',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='avis',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # CodePromo
        migrations.AddField(
            model_name='codepromo',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='codepromo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='codepromo',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Favoris
        migrations.AddField(
            model_name='favoris',
            name='statut',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='favoris',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='favoris',
            name='last_updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),

        # Ajustement final des champs created_at pour supprimer les valeurs par défaut temporaires
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='produit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='categorieproduit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='commande',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='livraison',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='mode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='panier',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='ville',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='commune',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='adresse',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='variationproduit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='avis',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='codepromo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='favoris',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]