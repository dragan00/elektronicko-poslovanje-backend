# Generated by Django 3.2.6 on 2021-09-08 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0029_rename_stock_equipments_stock_stock_equipment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='OIB',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
    ]
