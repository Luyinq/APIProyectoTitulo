# Generated by Django 4.1.7 on 2023-04-30 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PTitulo', '0015_alter_anuncio_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anuncio',
            name='fecha',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha'),
        ),
    ]