# Generated by Django 4.2.1 on 2024-10-16 08:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0033_order_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPCOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_id', models.CharField(max_length=100)),
                ('razorpay_order_id', models.CharField(max_length=100)),
                ('cpu', models.CharField(max_length=100)),
                ('gpu', models.CharField(max_length=100)),
                ('ram', models.CharField(max_length=100)),
                ('storage', models.CharField(max_length=100)),
                ('motherboard', models.CharField(max_length=100)),
                ('power_supply', models.CharField(max_length=100)),
                ('case', models.CharField(max_length=100)),
                ('wifi_card', models.CharField(blank=True, max_length=100, null=True)),
                ('bluetooth_card', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userapp.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
