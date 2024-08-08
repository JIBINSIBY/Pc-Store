# Generated by Django 5.0.6 on 2024-08-05 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0007_product_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('componentId', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stockLevel', models.IntegerField()),
                ('description', models.TextField()),
            ],
        ),
    ]
