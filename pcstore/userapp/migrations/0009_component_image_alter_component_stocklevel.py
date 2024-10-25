# Generated by Django 4.2.1 on 2024-08-05 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0008_component'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='component_images/'),
        ),
        migrations.AlterField(
            model_name='component',
            name='stockLevel',
            field=models.PositiveIntegerField(),
        ),
    ]
