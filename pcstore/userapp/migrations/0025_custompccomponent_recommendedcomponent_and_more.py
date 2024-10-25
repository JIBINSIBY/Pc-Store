# Generated by Django 4.2.1 on 2024-09-03 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0024_alter_custompc_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='custompccomponent',
            name='recommendedcomponent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recommended_for', to='userapp.component'),
        ),
        migrations.AlterField(
            model_name='custompccomponent',
            name='component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_components', to='userapp.component'),
        ),
    ]