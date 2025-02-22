# Generated by Django 4.2.1 on 2025-02-05 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0050_alter_delivery_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='status',
            field=models.CharField(choices=[('assigned', 'Assigned'), ('declined', 'Declined Assignment'), ('acceptedassigned', 'Accepted Assignment'), ('onway', 'On The Way'), ('delivered', 'Delivered')], default='assigned', max_length=100),
        ),
    ]
