# Generated by Django 5.1.6 on 2025-03-31 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0002_alter_proveedor_direccion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proveedor',
            name='direccion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
