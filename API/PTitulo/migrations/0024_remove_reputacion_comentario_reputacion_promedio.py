# Generated by Django 4.1.7 on 2023-06-29 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PTitulo', '0023_alter_usuario_msgtoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reputacion',
            name='comentario',
        ),
        migrations.AddField(
            model_name='reputacion',
            name='promedio',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]