# Generated by Django 4.2 on 2025-04-11 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличные'), ('card', 'Карта')], db_index=True, default='cash', max_length=20, verbose_name='Способ оплаты'),
        ),
    ]
