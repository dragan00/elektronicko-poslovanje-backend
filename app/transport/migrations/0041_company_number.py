# Generated by Django 3.2.7 on 2021-11-25 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0040_auto_20211115_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='number',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
