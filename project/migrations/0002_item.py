# Generated by Django 2.2 on 2023-04-06 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('i_type', models.CharField(max_length=250)),
                ('manufacturer', models.CharField(max_length=250)),
                ('v_type', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
            ],
        ),
    ]