# Generated by Django 4.2.7 on 2023-12-21 05:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_productimage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="total_price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
