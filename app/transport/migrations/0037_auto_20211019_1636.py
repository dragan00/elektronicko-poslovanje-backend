# Generated by Django 3.2.7 on 2021-10-19 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0036_cargo_closed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadingspace',
            name='closed_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='closed_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
