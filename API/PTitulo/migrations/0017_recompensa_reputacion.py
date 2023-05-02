# Generated by Django 4.1.7 on 2023-05-02 23:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('PTitulo', '0016_alter_anuncio_fecha'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recompensa',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=100, unique=True)),
                ('expiracion', models.DateField()),
                ('descripcion', models.TextField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reputacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.FloatField()),
                ('comentario', models.TextField()),
                ('evaluador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reputaciones_emitidas', to=settings.AUTH_USER_MODEL)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reputaciones_recibidas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('usuario', 'evaluador')},
            },
        ),
    ]
