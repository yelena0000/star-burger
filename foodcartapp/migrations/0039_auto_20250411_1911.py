# Generated by Django 4.2 on 2025-04-11 16:11

from django.db import migrations, models
from decimal import Decimal
from django.core.validators import MinValueValidator

def fill_orderitem_price(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')
    Product = apps.get_model('foodcartapp', 'Product')

    for item in OrderItem.objects.select_related('product'):
        item.price = item.product.price
        item.save(update_fields=['price'])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(
                verbose_name='цена за единицу',
                max_digits=8,
                decimal_places=2,
                null=True,
                validators=[MinValueValidator(Decimal('0.01'))]
            ),
        ),

        migrations.RunPython(fill_orderitem_price, reverse_code=migrations.RunPython.noop),

        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(
                verbose_name='цена за единицу',
                max_digits=8,
                decimal_places=2,
                validators=[MinValueValidator(Decimal('0.01'))]
            ),
        ),
    ]
