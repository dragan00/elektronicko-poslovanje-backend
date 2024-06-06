# Generated by Django 3.2.6 on 2021-08-10 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0006_stock_stockequipment_stocktype'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='company',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.company'),
        ),
    ]