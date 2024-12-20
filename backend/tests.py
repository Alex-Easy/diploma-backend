import os

import pytest
from django.contrib.auth import get_user_model
from .models import Shop, Category, Product, ProductInfo, Order, OrderItem, Contact
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }


@pytest.fixture
def user(user_data):
    User = get_user_model()
    return User.objects.create_user(**user_data)


@pytest.fixture
def shop():
    return Shop.objects.create(name="Test Shop", url="http://testshop.com")


@pytest.fixture
def category():
    return Category.objects.create(name="Electronics")


@pytest.mark.django_db
def test_create_user(user_data):
    User = get_user_model()
    user = User.objects.create_user(**user_data)
    assert user.username == user_data['username']
    assert user.email == user_data['email']


@pytest.mark.django_db
def test_create_superuser(user_data):
    User = get_user_model()
    superuser = User.objects.create_superuser(username="admin", email="admin@example.com", password="password")
    assert superuser.is_superuser


@pytest.mark.django_db
def test_create_shop(shop):
    assert shop.name == "Test Shop"
    assert shop.url == "http://testshop.com"


@pytest.mark.django_db
def test_create_category(category):
    assert category.name == "Electronics"


@pytest.mark.django_db
def test_product_info_clean(shop, category):
    product = Product.objects.create(name="Test Product", category=category)
    product_info = ProductInfo.objects.create(
        product=product,
        shop=shop,
        quantity=10,
        price=100,
        price_rrc=90
    )
    assert product_info.product.name == "Test Product"
    assert product_info.shop.name == "Test Shop"
    assert product_info.quantity == 10


@pytest.mark.django_db
def test_create_order(user, shop):
    order = Order.objects.create(user=user, status="new")
    assert order.user.username == user.username
    assert order.status == "new"


@pytest.mark.django_db
def test_create_order_item(user, shop, category):
    product = Product.objects.create(name="Test Product", category=category)
    order = Order.objects.create(user=user, status="new")
    order_item = OrderItem.objects.create(order=order, product=product, quantity=1, shop=shop)
    assert order_item.order == order
    assert order_item.product == product
    assert order_item.quantity == 1
    assert order_item.shop == shop


@pytest.mark.django_db
def test_create_contact(user):
    contact = Contact.objects.create(user=user, city="Test City", street="Test Street", house="1", apartment="101",
                                     phone="1234567890")
    assert contact.city == "Test City"
    assert contact.phone == "1234567890"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username='testuser', password='password123')
    return user


@pytest.fixture
def shop():
    from .models import Shop
    shop = Shop.objects.create(name='Test Shop', url='http://testshop.com')
    return shop


@pytest.fixture
def category():
    from .models import Category
    category = Category.objects.create(name='Electronics')
    return category


@pytest.fixture
def product():
    from .models import Product
    product = Product.objects.create(name='Test Product', category_id=1)
    return product


@pytest.fixture
def product_info():
    from .models import ProductInfo
    product_info = ProductInfo.objects.create(product_id=1, shop_id=1, quantity=10, price=100, price_rrc=90)
    return product_info


# @pytest.mark.django_db
# def test_import_products_success(api_client, user, shop, category, product, product_info):
#     api_client.force_authenticate(user=user)
#     url = reverse('import_products')
#     data = {
#         'shop': {
#             'name': 'Связной',
#             'url': 'http://svyaznoy.ru'
#         },
#         'categories': [
#             {
#                 'id': 224,
#                 'name': 'Смартфоны'
#             }
#         ],
#         'goods': [
#             {
#                 'id': 4216292,
#                 'category': 224,
#                 'name': 'Смартфон Apple iPhone XS Max 512GB (золотистый)',
#                 'price': 110000,
#                 'price_rrc': 116990,
#                 'quantity': 14
#             }
#         ]
#     }
#     response = api_client.post(url, data, format='json')
#     assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_import_products_no_file_provided(api_client, user, shop, category, product, product_info):
    api_client.force_authenticate(user=user)
    url = reverse('import_products')
    response = api_client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_import_products_invalid_yaml_format(api_client, user, shop, category, product, product_info):
    api_client.force_authenticate(user=user)
    url = reverse('import_products')
    data = """
    products:
      - name: "Test Product 1"
      - quantity: 50
      - price: 1000
    """
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
