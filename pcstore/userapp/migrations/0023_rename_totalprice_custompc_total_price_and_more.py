# Generated by Django 4.2.1 on 2024-09-01 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0022_custompc_approval_status_custompc_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='custompc',
            old_name='totalPrice',
            new_name='total_price',
        ),
        migrations.RenameField(
            model_name='custompc',
            old_name='userId',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='custompccomponent',
            old_name='config',
            new_name='custom_pc',
        ),
        migrations.AlterUniqueTogether(
            name='custompccomponent',
            unique_together={('custom_pc', 'component')},
        ),
        migrations.RemoveField(
            model_name='custompc',
            name='approval_status',
        ),
        migrations.RemoveField(
            model_name='custompc',
            name='configId',
        ),
        migrations.AddField(
            model_name='custompc',
            name='id',
            field=models.BigAutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='custompc',
            name='status',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='custompccomponent',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='custompc',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]