# Generated by Django 3.2.6 on 2021-08-26 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0014_auto_20210826_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='companydocument',
            name='company',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='company_documents', to='transport.company'),
            preserve_default=False,
        ),
    ]
