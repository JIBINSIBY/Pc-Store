# Generated by Django 4.2.1 on 2024-09-04 08:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0026_alter_custompccomponent_recommendedcomponent'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPCMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('custom_pc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='userapp.custompc')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
