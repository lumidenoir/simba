# Generated by Django 5.1.4 on 2024-12-25 13:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0011_sale_sale_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="sale",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="sale",
            name="customer_name",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]