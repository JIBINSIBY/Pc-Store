# Generated by Django 4.2.1 on 2024-09-04 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0027_custompcmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='custompcmessage',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
