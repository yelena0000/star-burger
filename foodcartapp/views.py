import json
from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt


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

@csrf_exempt
def register_order(request):
    #if request.method != 'POST':
    #    return JsonResponse({'error': 'Only POST allowed'}, status=405)

    order_details = json.loads(request.body)

    order = Order.objects.create(
        firstname=order_details['firstname'],
        lastname=order_details['lastname'],
        phonenumber=order_details['phonenumber'],
        address=order_details['address'],
    )

    for item in order_details['products']:
        product = Product.objects.get(pk=item['product'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity']
        )

    return JsonResponse({'order_id': order.id})
