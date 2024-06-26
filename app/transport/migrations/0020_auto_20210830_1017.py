# Generated by Django 3.2.6 on 2021-08-30 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0019_alter_company_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodstype',
            name='name',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='vehiclefeature',
            name='name',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='vehicletype',
            name='name',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='vehicleupgrade',
            name='name',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
