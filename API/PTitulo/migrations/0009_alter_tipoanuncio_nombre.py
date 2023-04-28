# Generated by Django 4.1.7 on 2023-04-28 01:47

import PTitulo.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PTitulo', '0008_alter_estado_nombre_alter_tipoanuncio_nombre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipoanuncio',
            name='nombre',
            field=models.CharField(max_length=50, validators=[PTitulo.models.validate_min, PTitulo.models.validate_only_letters], verbose_name='Nombre'),
        ),
    ]
