# Generated by Django 5.1.5 on 2025-02-03 12:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255, verbose_name='Nom')),
                ('statut', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=256)),
                ('couverture', models.ImageField(upload_to='articles')),
                ('resume', models.TextField()),
                ('contenu', models.TextField()),
                ('est_publie', models.BooleanField(default=False)),
                ('date_de_publicatio', models.DateField()),
                ('statut', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('auteur_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auteur_article_ids', to=settings.AUTH_USER_MODEL)),
                ('categorie_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categorie_article_ids', to='blog.categorie', verbose_name='Catégorie')),
                ('tag_ids', models.ManyToManyField(related_name='tag_article_ids', to='blog.tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
        ),
        migrations.CreateModel(
            name='Commentaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu', models.TextField()),
                ('statut', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('article_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_commentaire_ids', to='blog.article')),
                ('auteur_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auteur_commentaire_ids', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Commentaire',
                'verbose_name_plural': 'Commentaires',
            },
        ),
    ]
