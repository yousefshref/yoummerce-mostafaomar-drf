# Generated by Django 4.2 on 2023-09-04 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_order_is_arrived'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='is_returned',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]