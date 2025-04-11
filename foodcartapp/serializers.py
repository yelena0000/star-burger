from rest_framework import serializers
from .models import Product

class OrderProductSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

class RegisterOrderSerializer(serializers.Serializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phonenumber = serializers.RegexField(regex=r'^\+79\d{9}$', error_messages={
        'invalid': 'Введен некорректный номер телефона.'
    })
    address = serializers.CharField()
    products = OrderProductSerializer(many=True, allow_empty=False)
