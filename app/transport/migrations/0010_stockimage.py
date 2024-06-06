# Generated by Django 3.2.6 on 2021-08-23 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0009_country_alpha2code'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]