# Generated by Django 5.1.4 on 2024-12-25 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0009_delete_min"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="signup",
            name="email",
        ),
        migrations.AddField(
            model_name="item",
            name="bulk_price",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="item",
            name="chef_price",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="item",
            name="retailer_price",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]