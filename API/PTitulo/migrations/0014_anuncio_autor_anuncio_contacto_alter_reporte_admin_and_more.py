# Generated by Django 4.1.7 on 2023-04-29 03:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PTitulo', '0013_reporte_respuesta'),
    ]

    operations = [
        migrations.AddField(
            model_name='anuncio',
            name='autor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='anuncio_autor', to='PTitulo.usuario', verbose_name='Usuario'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='anuncio',
            name='contacto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='anuncio_interesado', to='PTitulo.usuario', verbose_name='Contacto'),
        ),
        migrations.AlterField(
            model_name='reporte',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reporte_admin', to='PTitulo.usuario', verbose_name='Admin'),
        ),
        migrations.AlterField(
            model_name='reporte',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reporte_usuario', to='PTitulo.usuario', verbose_name='Usuario'),
        ),
    ]
