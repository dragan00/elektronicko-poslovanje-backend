# Generated by Django 3.2.6 on 2021-09-04 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0024_auto_20210904_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='vehicle_equipment',
            field=models.ManyToManyField(blank=True, to='transport.VehicleEquipment'),
        ),
        migrations.AddField(
            model_name='loadingspace',
            name='vehicle_equipment',
            field=models.ManyToManyField(blank=True, to='transport.VehicleEquipment'),
        ),
        migrations.AlterField(
            model_name='cargo',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'active'), ('closed', 'closed')], default='active', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='loadingspace',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'active'), ('closed', 'closed')], default='active', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'active'), ('closed', 'closed')], default='active', max_length=15, null=True),
        ),
    ]
