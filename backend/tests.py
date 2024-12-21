import pytest
from django.contrib.auth import get_user_model
from .models import Shop, Category, Product, ProductInfo, Order, OrderItem, Contact
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch


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


@pytest.fixture
def product(category):
    from .models import Product
    product = Product.objects.create(name="Test Product", category=category)
    return product


@pytest.fixture
def product_info(shop, category, product):
    from .models import ProductInfo
    product_info = ProductInfo.objects.create(
        product=product,
        shop=shop,
        quantity=10,
        price=100,
        price_rrc=90
    )
    return product_info


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
def authenticated_user(db):
    user_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    user = get_user_model().objects.create_user(**user_data)
    user.set_password('password123')
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


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


@pytest.mark.django_db
def test_product_list_returns_200_for_authenticated_users(api_client, user, product):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert isinstance(response.data, list)  # Данные возвращаются в виде списка
    assert len(response.data) > 0  # Проверка, что товары возвращаются


@pytest.mark.django_db
def test_product_list_returns_403_for_unauthenticated_users(api_client):
    response = api_client.get('/api/products/')
    assert response.status_code == 403  # Доступ запрещен для неавторизованных


@pytest.mark.django_db
def test_product_list_returns_empty_list_for_authenticated_users(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert isinstance(response.data, list)  # Данные возвращаются в виде списка
    assert len(response.data) == 0  # Проверка пустого списка


@pytest.mark.django_db
def test_add_to_cart_creates_cart_item_for_authenticated_users(api_client, user, product):
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/cart/', {'product': product.id, 'quantity': 2})
    assert response.status_code == 201  # Товар успешно добавлен
    assert isinstance(response.data, dict)  # Данные возвращаются в виде словаря
    assert 'id' in response.data  # Корзина создана


@pytest.mark.django_db
def test_get_cart_returns_200_for_authenticated_users(api_client, user, product):
    api_client.force_authenticate(user=user)
    api_client.post('/api/cart/', {'product': product.id, 'quantity': 2})  # Добавляем товар
    response = api_client.get('/api/cart/')
    assert response.status_code == 200
    assert isinstance(response.data, list)  # Данные возвращаются в виде словаря
    assert len(response.data) > 0  # Проверка, что корзина не пуста


@pytest.mark.django_db
def test_remove_from_cart_deletes_cart_item_for_authenticated_users(api_client, user, product):
    api_client.force_authenticate(user=user)
    cart_item = api_client.post('/api/cart/', {'product': product.id, 'quantity': 2}).data
    response = api_client.delete(f'/api/cart/{cart_item["id"]}/')
    assert response.status_code == 204  # Товар успешно удален из корзины


# Тест на получение списка контактов
@pytest.mark.django_db
def test_get_contact_list(authenticated_user, contact):
    api_client, user = authenticated_user
    url = reverse('contact_list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Проверка, что возвращены данные


# Тест на получение контакта по ID
@pytest.mark.django_db
def test_get_contact_detail(authenticated_user, contact):
    api_client, user = authenticated_user
    url = reverse('contact_detail', args=[contact.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['city'] == contact.city


# Тест на обновление контакта
@pytest.mark.django_db
def test_update_contact(authenticated_user, contact):
    api_client, user = authenticated_user
    data = {'city': 'Updated City'}
    url = reverse('contact_detail', args=[contact.id])
    response = api_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['city'] == 'Updated City'


# Тест на удаление контакта
@pytest.mark.django_db
def test_delete_contact(authenticated_user, contact):
    api_client, user = authenticated_user
    url = reverse('contact_detail', args=[contact.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Contact.objects.filter(id=contact.id).exists()


@pytest.mark.django_db
def test_confirm_order(api_client, user, order):
    # Аутентификация пользователя
    api_client.force_authenticate(user=user)

    # Подтверждение заказа
    url = reverse('order_confirm', args=[order.id])
    response = api_client.post(url)

    # Проверка успешного подтверждения
    assert response.status_code == status.HTTP_200_OK
    order.refresh_from_db()
    assert order.status == 'confirmed'


@pytest.mark.django_db
def test_confirm_order_unauthorized(api_client, order):
    # Попытка подтвердить заказ без авторизации
    url = reverse('order_confirm', args=[order.id])
    response = api_client.post(url)

    # Проверка, что неавторизованный пользователь не может подтвердить заказ
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_confirm_order_not_found(api_client, user):
    # Попытка подтвердить несуществующий заказ
    api_client.force_authenticate(user=user)
    url = reverse('order_confirm', args=[99999])  # Не существует заказа с таким ID
    response = api_client.post(url)

    # Проверка, что заказ не найден
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_order_list(api_client, user, order):
    # Аутентификация пользователя
    api_client.force_authenticate(user=user)

    # Получение списка заказов
    url = reverse('order_list')
    response = api_client.get(url)

    # Проверка, что заказ в списке
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Должен быть хотя бы один заказ
    assert response.data[0]['id'] == order.id  # Проверяем наличие правильного заказа


@pytest.mark.django_db
def test_get_order_list_unauthorized(api_client):
    # Попытка получить список заказов без авторизации
    url = reverse('order_list')
    response = api_client.get(url)

    # Проверка, что неавторизованный пользователь не может получить список заказов
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_order_list_empty(api_client, user):
    # Проверка получения пустого списка заказов, если у пользователя нет заказов
    api_client.force_authenticate(user=user)
    url = reverse('order_list')
    response = api_client.get(url)

    # Проверка, что список заказов пуст
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0  # Список пуст


@pytest.mark.django_db
def test_order_detail_authenticated_user(api_client, user, order, order_item):
    api_client.force_authenticate(user=user)
    response = api_client.get(f'/api/orders/{order.id}/')
    assert response.status_code == 200
    assert response.data['id'] == order.id
    assert response.data['status'] == order.status


@pytest.mark.django_db
def test_order_detail_unauthorized_user(api_client, order):
    response = api_client.get(f'/api/orders/{order.id}/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_order_detail_not_found(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/orders/999/')
    assert response.status_code == 404
    assert response.data['detail'] == "Not found."


@pytest.fixture
def order(user):
    return Order.objects.create(user=user, status="new")


@pytest.mark.django_db
def test_update_order_status_authenticated_user(api_client, user, order):
    api_client.force_authenticate(user=user)
    url = reverse('order_status_update', kwargs={'order_id': order.id})
    data = {"status": "confirmed"}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == "confirmed"
    order.refresh_from_db()
    assert order.status == "confirmed"


@pytest.mark.django_db
def test_update_order_status_unauthenticated_user(api_client, order):
    url = reverse('order_status_update', kwargs={'order_id': order.id})
    data = {"status": "confirmed"}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_order_status_invalid_status(api_client, user, order):
    api_client.force_authenticate(user=user)
    url = reverse('order_status_update', kwargs={'order_id': order.id})
    data = {"status": "invalid_status"}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Некорректный статус" in str(response.data)


@pytest.mark.django_db
def test_update_order_status_other_user(api_client, user, another_user, order):
    api_client.force_authenticate(user=another_user)
    url = reverse('order_status_update', kwargs={'order_id': order.id})
    data = {"status": "confirmed"}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@patch('django.core.mail.send_mail')
def test_order_confirmation_email_sent(mock_send_mail, api_client, user, order):
    api_client.force_authenticate(user=user)
    url = reverse('order_status_update', kwargs={'order_id': order.id})
    data = {"status": "confirmed"}

    response = api_client.patch(url, data, format='json')

    # Проверка успешного изменения статуса заказа
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == "confirmed"

    # Проверяем, что email был отправлен
    mock_send_mail.assert_called_once_with(
        'Подтверждение заказа',
        f'Ваш заказ #{order.id} был подтвержден. Спасибо за покупку!',
        'test@example.com',
        [user.email]
    )


@pytest.mark.django_db
def test_get_product_detail_success(api_client, product_info):
    url = reverse('product_detail', args=[product_info.product.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['product'] == product_info.product.id
    assert response.data['price'] == product_info.price
    assert response.data['quantity'] == product_info.quantity


@pytest.mark.django_db
def test_get_product_detail_not_found(api_client):
    url = reverse('product_detail', args=[9999])  # Несуществующий продукт
    response = api_client.get(url)
    assert response.status_code == 404
    assert response.data['detail'] == 'Product not found.'
