# Generated by Django 4.2 on 2023-08-18 00:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='header',
            name='header_products',
        ),
        migrations.DeleteModel(
            name='CustomHome',
        ),
        migrations.DeleteModel(
            name='Header',
        ),
    ]