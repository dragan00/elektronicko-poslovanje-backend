# Generated by Django 3.2.7 on 2021-10-29 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0038_auto_20211025_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='alpha2Code',
            field=models.CharField(blank=True, default=None, max_length=4, null=True),
        ),
    ]
