# Generated by Django 4.2.1 on 2024-09-03 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0025_custompccomponent_recommendedcomponent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custompccomponent',
            name='recommendedcomponent',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
