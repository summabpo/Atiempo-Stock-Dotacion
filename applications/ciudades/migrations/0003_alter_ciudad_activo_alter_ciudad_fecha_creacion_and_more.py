# Generated by Django 5.1.6 on 2025-02-24 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ciudades', '0002_ciudad_id_usuario_insert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ciudad',
            name='activo',
            field=models.BooleanField(default=True, verbose_name='Activo/Inactivo'),
        ),
        migrations.AlterField(
            model_name='ciudad',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación'),
        ),
        migrations.AlterField(
            model_name='ciudad',
            name='nombre',
            field=models.CharField(max_length=255, verbose_name='Nombre de la ciudad'),
        ),
    ]
