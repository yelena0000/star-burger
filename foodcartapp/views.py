from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from geolocation.models import Place
from geolocation.utils import resolve_coordinates

from .models import Product
from .serializers import OrderSerializer
from .serializers import RegisterOrderSerializer


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
    serializer = RegisterOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            order = serializer.save()

            address = order.address
            place = Place.objects.filter(address=address).first()

            if not place or place.latitude is None or place.longitude is None:
                coords = resolve_coordinates(address, settings.YANDEX_GEOCODER_API_KEY)
                latitude, longitude = coords if coords else (None, None)

                Place.objects.update_or_create(
                    address=address,
                    defaults={
                        'latitude': latitude,
                        'longitude': longitude
                    }
                )

    except Exception as error:
        return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response_serializer = OrderSerializer(order)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
