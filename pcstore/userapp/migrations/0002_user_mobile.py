# Generated by Django 4.2.1 on 2024-07-09 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mobile',
            field=models.CharField(default='nil', max_length=20),
        ),
    ]
