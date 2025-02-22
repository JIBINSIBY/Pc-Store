# Generated by Django 4.2.1 on 2025-01-28 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0045_user_is_deliveryboy'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryBoy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_number', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('on_delivery', 'On Delivery'), ('offline', 'Offline')], default='available', max_length=100)),
                ('joined_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Delivery Boy',
                'verbose_name_plural': 'Delivery Boys',
            },
        ),
    ]
