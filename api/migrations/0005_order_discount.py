# Generated by Django 4.2 on 2023-08-18 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_order_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
