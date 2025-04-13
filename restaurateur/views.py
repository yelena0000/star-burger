from geopy.distance import distance

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from foodcartapp.models import Order
from foodcartapp.models import Product
from foodcartapp.models import Restaurant

from geolocation.models import Place
from geolocation.utils import resolve_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = (
        Order.objects
        .exclude(status=Order.OrderStatus.COMPLETED)
        .with_total_price()
        .select_related('assigned_restaurant')
        .prefetch_related('items__product')
    )

    geocoder_apikey = settings.YANDEX_GEOCODER_API_KEY

    addresses = set()
    for order in orders:
        addresses.add(order.address)

    all_restaurants = list(Restaurant.objects.all())
    for restaurant in all_restaurants:
        addresses.add(restaurant.address)

    places = Place.objects.filter(address__in=addresses)
    coordinates_cache = {place.address: (place.latitude, place.longitude) for place in places}

    orders_with_restaurants = []

    for order in orders:
        order_products = order.items.all()

        available_restaurants = Restaurant.objects.filter(
            menu_items__product__in=[item.product for item in order_products],
            menu_items__availability=True
        ).distinct()

        valid_restaurants = []

        order_coords = resolve_coordinates(order.address, geocoder_apikey, coordinates_cache)

        for restaurant in available_restaurants:
            can_prepare_all = all(
                restaurant.menu_items.filter(
                    product=item.product,
                    availability=True
                ).exists()
                for item in order_products
            )
            if not can_prepare_all:
                continue

            rest_coords = resolve_coordinates(restaurant.address, geocoder_apikey, coordinates_cache)

            if order_coords and rest_coords:
                try:
                    dist = distance(
                        order_coords,
                        rest_coords
                    ).km
                    valid_restaurants.append({
                        'restaurant': restaurant,
                        'distance': round(dist, 1)
                    })
                except Exception as e:
                    valid_restaurants.append({
                        'restaurant': restaurant,
                        'distance': None
                    })
            else:
                valid_restaurants.append({
                    'restaurant': restaurant,
                    'distance': None
                })

        sorted_restaurants = sorted(
            valid_restaurants,
            key=lambda x: x['distance'] if x['distance'] is not None else float('inf')
        )

        orders_with_restaurants.append({
            'order': order,
            'restaurants': sorted_restaurants,
        })

    return render(request, 'order_items.html', {
        'orders_with_restaurants': orders_with_restaurants,
    })
