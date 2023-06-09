# Generated by Django 4.1.7 on 2023-06-05 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PTitulo', '0017_recompensa_reputacion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='anuncio',
            old_name='descripción',
            new_name='descripcion',
        ),
        migrations.AlterField(
            model_name='posicion',
            name='latitud',
            field=models.FloatField(verbose_name='Latitud'),
        ),
        migrations.AlterField(
            model_name='posicion',
            name='longitud',
            field=models.FloatField(verbose_name='Longitud'),
        ),
    ]
