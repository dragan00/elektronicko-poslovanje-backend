# Generated by Django 3.2.6 on 2021-08-26 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_account_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='avatar',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='images/'),
        ),
    ]
