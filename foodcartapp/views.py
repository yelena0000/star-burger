import json
import re
from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Order
from .models import OrderItem
from .models import Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_details = request.data
    errors = {}

    if 'products' not in order_details:
        errors['products'] = 'Обязательное поле.'
    else:
        products = order_details['products']
        if products is None:
            errors['products'] = 'Это поле не может быть пустым.'
        elif not isinstance(products, list):
            errors['products'] = 'Ожидался list со значениями, но был получен "str".'
        elif not products:
            errors['products'] = 'Этот список не может быть пустым.'
        else:
            for index, item in enumerate(products):
                if not isinstance(item, dict):
                    errors['products'] = f'Элемент #{index+1} должен быть словарём.'
                    break
                if 'product' not in item or 'quantity' not in item:
                    errors['products'] = f'Элемент #{index+1} должен содержать ключи "product" и "quantity".'
                    break
                try:
                    product_id = int(item['product'])
                    Product.objects.get(id=product_id)
                except (ValueError, Product.DoesNotExist):
                    errors['products'] = f'Недопустимый первичный ключ "{item.get("product")}"'
                    break
                try:
                    quantity = int(item['quantity'])
                    if quantity <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    errors['products'] = f'Недопустимое количество для товара #{index+1}.'
                    break

    for field in ['firstname', 'lastname', 'phonenumber', 'address']:
        if field not in order_details:
            errors[field] = 'Обязательное поле.'
            continue

        value = order_details[field]

        if value is None or not isinstance(value, str) or not value.strip():
            errors[field] = 'Это поле не может быть пустым.'

    phonenumber = order_details.get('phonenumber')
    if isinstance(phonenumber, str) and not re.fullmatch(r'\+79\d{9}', phonenumber.strip()):
        errors['phonenumber'] = 'Введен некорректный номер телефона.'

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=order_details['firstname'].strip(),
        lastname=order_details['lastname'].strip(),
        phonenumber=phonenumber.strip(),
        address=order_details['address'].strip()
    )

    for item in order_details['products']:
        product = Product.objects.get(id=item['product'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity']
        )

    return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
