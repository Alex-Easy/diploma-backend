import pytest
from django.contrib.auth import get_user_model
from .models import Shop, Category, Product, ProductInfo, Order, OrderItem, Contact


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