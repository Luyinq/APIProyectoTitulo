# Generated by Django 4.0.4 on 2023-04-11 23:35

import PTitulo.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('rut', models.IntegerField(primary_key=True, serialize=False, validators=[PTitulo.models.validate_chilean_rut], verbose_name='Rut')),
                ('nombre', models.CharField(max_length=20, verbose_name='Nombre')),
                ('apellido', models.CharField(max_length=20, verbose_name='Apellido')),
                ('contrasena', models.CharField(max_length=128, verbose_name='Contraseña')),
                ('correo', models.EmailField(max_length=128, unique=True, verbose_name='Correo')),
                ('foto', models.CharField(blank=True, default=None, max_length=256, null=True, verbose_name='Foto')),
                ('celular', models.IntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(999999999), django.core.validators.MinValueValidator(900000000)], verbose_name='Celular')),
                ('isActive', models.BooleanField(default=True, verbose_name='Activo')),
                ('isAdmin', models.BooleanField(default=False, verbose_name='Admin')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]