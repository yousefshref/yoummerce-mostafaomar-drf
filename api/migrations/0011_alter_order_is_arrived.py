# Generated by Django 4.2 on 2023-09-04 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_order_phone2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='is_arrived',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='is_arrived', to='api.shipped'),
        ),
    ]
