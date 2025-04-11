# Generated by Django 4.2 on 2025-04-11 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_order_called_at_order_created_at_order_delivered_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='called_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='delivered_at',
        ),
        migrations.AddField(
            model_name='order',
            name='call_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата звонка'),
        ),
        migrations.AddField(
            model_name='order',
            name='deliver_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата и время создания'),
        ),
    ]
