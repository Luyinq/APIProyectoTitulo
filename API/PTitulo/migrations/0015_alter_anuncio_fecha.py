# Generated by Django 4.1.7 on 2023-04-30 18:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('PTitulo', '0014_anuncio_autor_anuncio_contacto_alter_reporte_admin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anuncio',
            name='fecha',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha'),
        ),
    ]
