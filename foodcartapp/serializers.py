from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import Order, OrderItem, Product


class OrderProductSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class RegisterOrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        order_items = [
            OrderItem(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
            for item in products_data
        ]
        OrderItem.objects.bulk_create(order_items)

        return order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address']
