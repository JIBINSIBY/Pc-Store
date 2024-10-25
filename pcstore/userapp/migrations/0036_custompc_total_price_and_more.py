# Generated by Django 4.2.1 on 2024-10-17 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0035_rename_order_date_custompcorder_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='custompc',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='custompccomponent',
            name='custom_pc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_components', to='userapp.custompc'),
        ),
    ]
