# Generated by Django 4.2.1 on 2024-08-24 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0016_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
