# Generated by Django 4.2.20 on 2025-04-28 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_discount_shipment_cart_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='kefir',
        ),
        migrations.RemoveField(
            model_name='shipment',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='shipment',
            name='manager',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
        migrations.DeleteModel(
            name='Discount',
        ),
        migrations.DeleteModel(
            name='Shipment',
        ),
    ]
