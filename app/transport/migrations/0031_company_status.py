# Generated by Django 3.2.6 on 2021-09-14 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0030_alter_company_oib'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'active'), ('need_confirm', 'need_confirm')], default='need_confirm', max_length=15, null=True),
        ),
    ]
