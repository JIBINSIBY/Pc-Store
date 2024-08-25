# Generated by Django 4.2.1 on 2024-08-24 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0019_remove_rating_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='rating',
            name='description',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]