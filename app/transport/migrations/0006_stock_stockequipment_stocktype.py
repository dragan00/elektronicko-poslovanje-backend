# Generated by Django 3.2.6 on 2021-08-10 08:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transport', '0005_loadingspace_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockEquipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.JSONField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.JSONField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField(blank=True, default=None, null=True)),
                ('end_datetime', models.DateTimeField(blank=True, default=None, null=True)),
                ('min_area', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=11, null=True)),
                ('max_area', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=11, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(blank=True, default=None, max_length=20, null=True)),
                ('city', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.city')),
                ('contact_accounts', models.ManyToManyField(blank=True, related_name='stock_contact_accounts', to=settings.AUTH_USER_MODEL)),
                ('country', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.country')),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('stock_equipments', models.ManyToManyField(blank=True, to='transport.StockEquipment')),
                ('stock_types', models.ManyToManyField(blank=True, to='transport.StockType')),
                ('zip_code', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.zipcode')),
            ],
        ),
    ]
