# import pytest
# from django.contrib.auth import get_user_model
# from .models import Shop, Category, Product, ProductInfo, Order, OrderItem, Contact
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from unittest.mock import patch
#
#
# @pytest.fixture
# def user_data():
#     return {
#         'username': 'testuser',
#         'email': 'testuser@example.com',
#         'password': 'password123'
#     }
#
#
# @pytest.fixture
# def user(user_data):
#     User = get_user_model()
#     return User.objects.create_user(**user_data)
#
#
# @pytest.fixture
# def shop():
#     return Shop.objects.create(name="Test Shop", url="http://testshop.com")
#
#
# @pytest.fixture
# def category():
#     return Category.objects.create(name="Electronics")
#
#
# @pytest.fixture
# def product(category):
#     from .models import Product
#     product = Product.objects.create(name="Test Product", category=category)
#     return product
#
#
# @pytest.fixture
# def product_info(shop, category, product):
#     from .models import ProductInfo
#     product_info = ProductInfo.objects.create(
#         product=product,
#         shop=shop,
#         quantity=10,
#         price=100,
#         price_rrc=90
#     )
#     return product_info
#
#
# @pytest.mark.django_db
# def test_create_user(user_data):
#     User = get_user_model()
#     user = User.objects.create_user(**user_data)
#     assert user.username == user_data['username']
#     assert user.email == user_data['email']
#
#
# @pytest.mark.django_db
# def test_create_superuser(user_data):
#     User = get_user_model()
#     superuser = User.objects.create_superuser(username="admin", email="admin@example.com", password="password")
#     assert superuser.is_superuser
#
#
# @pytest.mark.django_db
# def test_create_shop(shop):
#     assert shop.name == "Test Shop"
#     assert shop.url == "http://testshop.com"
#
#
# @pytest.mark.django_db
# def test_create_category(category):
#     assert category.name == "Electronics"
#
#
# @pytest.mark.django_db
# def test_product_info_clean(shop, category):
#     product = Product.objects.create(name="Test Product", category=category)
#     product_info = ProductInfo.objects.create(
#         product=product,
#         shop=shop,
#         quantity=10,
#         price=100,
#         price_rrc=90
#     )
#     assert product_info.product.name == "Test Product"
#     assert product_info.shop.name == "Test Shop"
#     assert product_info.quantity == 10
#
#
# @pytest.mark.django_db
# def test_create_order(user, shop):
#     order = Order.objects.create(user=user, status="new")
#     assert order.user.username == user.username
#     assert order.status == "new"
#
#
# @pytest.mark.django_db
# def test_create_order_item(user, shop, category):
#     product = Product.objects.create(name="Test Product", category=category)
#     order = Order.objects.create(user=user, status="new")
#     order_item = OrderItem.objects.create(order=order, product=product, quantity=1, shop=shop)
#     assert order_item.order == order
#     assert order_item.product == product
#     assert order_item.quantity == 1
#     assert order_item.shop == shop
#
#
# @pytest.mark.django_db
# def test_create_contact(user):
#     contact = Contact.objects.create(user=user, city="Test City", street="Test Street", house="1", apartment="101",
#                                      phone="1234567890")
#     assert contact.city == "Test City"
#     assert contact.phone == "1234567890"
#
#
# @pytest.fixture
# def api_client():
#     return APIClient()
#
#
# @pytest.fixture
# def authenticated_user(db):
#     user_data = {
#         'username': 'testuser',
#         'email': 'testuser@example.com',
#         'password': 'password123',
#         'first_name': 'Test',
#         'last_name': 'User'
#     }
#     user = get_user_model().objects.create_user(**user_data)
#     user.set_password('password123')
#     user.save()
#     client = APIClient()
#     client.force_authenticate(user=user)
#     return client, user
#
#
# @pytest.mark.django_db
# def test_import_products_no_file_provided(api_client, user, shop, category, product, product_info):
#     api_client.force_authenticate(user=user)
#     url = reverse('import_products')
#     response = api_client.post(url, {}, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#
# @pytest.mark.django_db
# def test_import_products_invalid_yaml_format(api_client, user, shop, category, product, product_info):
#     api_client.force_authenticate(user=user)
#     url = reverse('import_products')
#     data = """
#     products:
#       - name: "Test Product 1"
#       - quantity: 50
#       - price: 1000
#     """
#     response = api_client.post(url, data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#
# @pytest.mark.django_db
# def test_product_list_returns_200_for_authenticated_users(api_client, user, product):
#     api_client.force_authenticate(user=user)
#     response = api_client.get('/api/products/')
#     assert response.status_code == 200
#     assert isinstance(response.data, list)  # Данные возвращаются в виде списка
#     assert len(response.data) > 0  # Проверка, что товары возвращаются
#
#
# @pytest.mark.django_db
# def test_product_list_returns_403_for_unauthenticated_users(api_client):
#     response = api_client.get('/api/products/')
#     assert response.status_code == 403  # Доступ запрещен для неавторизованных
#
#
# @pytest.mark.django_db
# def test_product_list_returns_empty_list_for_authenticated_users(api_client, user):
#     api_client.force_authenticate(user=user)
#     response = api_client.get('/api/products/')
#     assert response.status_code == 200
#     assert isinstance(response.data, list)  # Данные возвращаются в виде списка
#     assert len(response.data) == 0  # Проверка пустого списка
#
#
# @pytest.mark.django_db
# def test_add_to_cart_creates_cart_item_for_authenticated_users(api_client, user, product):
#     api_client.force_authenticate(user=user)
#     response = api_client.post('/api/cart/', {'product': product.id, 'quantity': 2})
#     assert response.status_code == 201  # Товар успешно добавлен
#     assert isinstance(response.data, dict)  # Данные возвращаются в виде словаря
#     assert 'id' in response.data  # Корзина создана
#
#
# @pytest.mark.django_db
# def test_get_cart_returns_200_for_authenticated_users(api_client, user, product):
#     api_client.force_authenticate(user=user)
#     api_client.post('/api/cart/', {'product': product.id, 'quantity': 2})  # Добавляем товар
#     response = api_client.get('/api/cart/')
#     assert response.status_code == 200
#     assert isinstance(response.data, list)  # Данные возвращаются в виде словаря
#     assert len(response.data) > 0  # Проверка, что корзина не пуста
#
#
# @pytest.mark.django_db
# def test_remove_from_cart_deletes_cart_item_for_authenticated_users(api_client, user, product):
#     api_client.force_authenticate(user=user)
#     cart_item = api_client.post('/api/cart/', {'product': product.id, 'quantity': 2}).data
#     response = api_client.delete(f'/api/cart/{cart_item["id"]}/')
#     assert response.status_code == 204  # Товар успешно удален из корзины
#
#
# # Тест на получение списка контактов
# @pytest.mark.django_db
# def test_get_contact_list(authenticated_user, contact):
#     api_client, user = authenticated_user
#     url = reverse('contact_list')
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) > 0  # Проверка, что возвращены данные
#
#
# # Тест на получение контакта по ID
# @pytest.mark.django_db
# def test_get_contact_detail(authenticated_user, contact):
#     api_client, user = authenticated_user
#     url = reverse('contact_detail', args=[contact.id])
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['city'] == contact.city
#
#
# # Тест на обновление контакта
# @pytest.mark.django_db
# def test_update_contact(authenticated_user, contact):
#     api_client, user = authenticated_user
#     data = {'city': 'Updated City'}
#     url = reverse('contact_detail', args=[contact.id])
#     response = api_client.put(url, data)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['city'] == 'Updated City'
#
#
# # Тест на удаление контакта
# @pytest.mark.django_db
# def test_delete_contact(authenticated_user, contact):
#     api_client, user = authenticated_user
#     url = reverse('contact_detail', args=[contact.id])
#     response = api_client.delete(url)
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert not Contact.objects.filter(id=contact.id).exists()
#
#
# @pytest.mark.django_db
# def test_confirm_order(api_client, user, order):
#     # Аутентификация пользователя
#     api_client.force_authenticate(user=user)
#
#     # Подтверждение заказа
#     url = reverse('order_confirm', args=[order.id])
#     response = api_client.post(url)
#
#     # Проверка успешного подтверждения
#     assert response.status_code == status.HTTP_200_OK
#     order.refresh_from_db()
#     assert order.status == 'confirmed'
#
#
# @pytest.mark.django_db
# def test_confirm_order_unauthorized(api_client, order):
#     # Попытка подтвердить заказ без авторизации
#     url = reverse('order_confirm', args=[order.id])
#     response = api_client.post(url)
#
#     # Проверка, что неавторизованный пользователь не может подтвердить заказ
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#
#
# @pytest.mark.django_db
# def test_confirm_order_not_found(api_client, user):
#     # Попытка подтвердить несуществующий заказ
#     api_client.force_authenticate(user=user)
#     url = reverse('order_confirm', args=[99999])  # Не существует заказа с таким ID
#     response = api_client.post(url)
#
#     # Проверка, что заказ не найден
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#
#
# @pytest.mark.django_db
# def test_get_order_list(api_client, user, order):
#     # Аутентификация пользователя
#     api_client.force_authenticate(user=user)
#
#     # Получение списка заказов
#     url = reverse('order_list')
#     response = api_client.get(url)
#
#     # Проверка, что заказ в списке
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) > 0  # Должен быть хотя бы один заказ
#     assert response.data[0]['id'] == order.id  # Проверяем наличие правильного заказа
#
#
# @pytest.mark.django_db
# def test_get_order_list_unauthorized(api_client):
#     # Попытка получить список заказов без авторизации
#     url = reverse('order_list')
#     response = api_client.get(url)
#
#     # Проверка, что неавторизованный пользователь не может получить список заказов
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#
#
# @pytest.mark.django_db
# def test_get_order_list_empty(api_client, user):
#     # Проверка получения пустого списка заказов, если у пользователя нет заказов
#     api_client.force_authenticate(user=user)
#     url = reverse('order_list')
#     response = api_client.get(url)
#
#     # Проверка, что список заказов пуст
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) == 0  # Список пуст
#
#
# @pytest.mark.django_db
# def test_order_detail_authenticated_user(api_client, user, order, order_item):
#     api_client.force_authenticate(user=user)
#     response = api_client.get(f'/api/orders/{order.id}/')
#     assert response.status_code == 200
#     assert response.data['id'] == order.id
#     assert response.data['status'] == order.status
#
#
# @pytest.mark.django_db
# def test_order_detail_unauthorized_user(api_client, order):
#     response = api_client.get(f'/api/orders/{order.id}/')
#     assert response.status_code == 403
#
#
# @pytest.mark.django_db
# def test_order_detail_not_found(api_client, user):
#     api_client.force_authenticate(user=user)
#     response = api_client.get('/api/orders/999/')
#     assert response.status_code == 404
#     assert response.data['detail'] == "Not found."
#
#
# @pytest.fixture
# def order(user):
#     return Order.objects.create(user=user, status="new")
#
#
# @pytest.mark.django_db
# def test_update_order_status_authenticated_user(api_client, user, order):
#     api_client.force_authenticate(user=user)
#     url = reverse('order_status_update', kwargs={'order_id': order.id})
#     data = {"status": "confirmed"}
#     response = api_client.patch(url, data, format='json')
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['status'] == "confirmed"
#     order.refresh_from_db()
#     assert order.status == "confirmed"
#
#
# @pytest.mark.django_db
# def test_update_order_status_unauthenticated_user(api_client, order):
#     url = reverse('order_status_update', kwargs={'order_id': order.id})
#     data = {"status": "confirmed"}
#     response = api_client.patch(url, data, format='json')
#
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# @pytest.mark.django_db
# def test_update_order_status_invalid_status(api_client, user, order):
#     api_client.force_authenticate(user=user)
#     url = reverse('order_status_update', kwargs={'order_id': order.id})
#     data = {"status": "invalid_status"}
#     response = api_client.patch(url, data, format='json')
#
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Некорректный статус" in str(response.data)
#
#
# @pytest.mark.django_db
# def test_update_order_status_other_user(api_client, user, another_user, order):
#     api_client.force_authenticate(user=another_user)
#     url = reverse('order_status_update', kwargs={'order_id': order.id})
#     data = {"status": "confirmed"}
#     response = api_client.patch(url, data, format='json')
#
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#
#
# @pytest.mark.django_db
# @patch('django.core.mail.send_mail')
# def test_order_confirmation_email_sent(mock_send_mail, api_client, user, order):
#     api_client.force_authenticate(user=user)
#     url = reverse('order_status_update', kwargs={'order_id': order.id})
#     data = {"status": "confirmed"}
#
#     response = api_client.patch(url, data, format='json')
#
#     # Проверка успешного изменения статуса заказа
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['status'] == "confirmed"
#
#     # Проверяем, что email был отправлен
#     mock_send_mail.assert_called_once_with(
#         'Подтверждение заказа',
#         f'Ваш заказ #{order.id} был подтвержден. Спасибо за покупку!',
#         'test@example.com',
#         [user.email]
#     )
#
#
# @pytest.mark.django_db
# def test_get_product_detail_success(api_client, product_info):
#     url = reverse('product_detail', args=[product_info.product.id])
#     response = api_client.get(url)
#     assert response.status_code == 200
#     assert response.data['product'] == product_info.product.id
#     assert response.data['price'] == product_info.price
#     assert response.data['quantity'] == product_info.quantity
#
#
# @pytest.mark.django_db
# def test_get_product_detail_not_found(api_client):
#     url = reverse('product_detail', args=[9999])  # Несуществующий продукт
#     response = api_client.get(url)
#     assert response.status_code == 404
#     assert response.data['detail'] == 'Product not found.'
#
#

# Тест для регистрации пользователя без подтверждения email

# import pytest
# from rest_framework import status
# from django.urls import reverse
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
#
#
# @pytest.fixture
# def api_client():
#     """Создание клиента для API, который будет использоваться в тестах."""
#     return APIClient()
#
#
# @pytest.fixture
# def user_data():
#     """Данные для регистрации пользователя."""
#     return {
#         "username": "test_user",
#         "email": "test_user@gmail.com",
#         "password": "password"
#     }
#
#
# @pytest.fixture
# def existing_user():
#     """Создание существующего пользователя для проверки уникальности email."""
#     user = get_user_model().objects.create_user(
#         username="existing_user",
#         email="test_user@gmail.com",
#         password="password"
#     )
#     return user
#
#
# @pytest.mark.django_db
# def test_register_user(api_client, user_data):
#     """Тестируем регистрацию нового пользователя."""
#     url = reverse('register')  # Используйте правильный URL из вашего `urls.py`
#
#     response = api_client.post(url, user_data, format='json')
#
#     # Проверка успешной регистрации (статус 201)
#     assert response.status_code == status.HTTP_201_CREATED
#
#     # Проверка, что пользователь был создан в базе данных
#     user = get_user_model().objects.filter(email=user_data['email']).first()
#     assert user is not None
#     assert user.email == user_data['email']
#     assert user.check_password(user_data['password'])
#
#
# @pytest.mark.django_db
# def test_register_user_with_existing_email(api_client, user_data, existing_user):
#     """Тестируем регистрацию с уже существующим email."""
#     user_data['email'] = existing_user.email  # Используем email существующего пользователя
#
#     response = api_client.post(reverse('register'), user_data, format='json')
#
#     # Проверка, что мы получили ошибку, так как email уже существует
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Этот email уже занят" in str(response.data)

# Тест для регистрации пользователя с подтверждением email (успешный случай)

# import pytest
# from django.core import mail
# from rest_framework import status
# from django.urls import reverse
# from django.contrib.auth import get_user_model
#
#
# @pytest.mark.django_db
# def test_user_registration_with_email_confirmation(client):
#     url = reverse('register_user')  # Укажите правильный URL для регистрации
#     data = {
#         'username': 'new_user_test',
#         'email': 'test@example.com',
#         'password': 'SecurePassword123'
#     }
#
#     # Отправляем запрос на регистрацию
#     response = client.post(url, data, format='json')
#
#     # Проверка, что ответ успешный
#     assert response.status_code == status.HTTP_201_CREATED
#     assert "Пользователь успешно зарегистрирован!" in response.data["Сообщение"]
#
#     # Проверка, что письмо отправлено
#     assert len(mail.outbox) == 1
#     email = mail.outbox[0]
#     assert 'Подтверждение электронной почты' in email.subject
#     assert 'test@example.com' in email.to
#
#     # Проверяем, что пользователь не активен до подтверждения email
#     user = get_user_model().objects.get(email='test@example.com')
#     assert not user.is_active

# Тест для регистрации пользователя с подтверждением email (кода email уже занят)

# @pytest.mark.django_db
# def test_user_registration_with_existing_email(client):
#     url = reverse('register_user')
#     existing_user = get_user_model().objects.create_user(
#         username='existing_user',
#         email='existing@example.com',
#         password='ExistingPassword123'
#     )
#
#     data = {
#         'username': 'new_user_test',
#         'email': 'existing@example.com',
#         'password': 'SecurePassword123'
#     }
#
#     # Попытка зарегистрировать нового пользователя с уже занятой почтой
#     response = client.post(url, data, format='json')
#
#     # Проверка, что возвращена ошибка с занятым email
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert 'Этот email уже занят.' in response.data['email']

# Тест для регистрации пользователя с подтверждением email (активация пользователя после подтверждения email)

# @pytest.mark.django_db
# def test_email_confirmation(client):
#     user = get_user_model().objects.create_user(
#         username='user_for_confirmation',
#         email='userforconfirm@example.com',
#         password='Password1234'
#     )
#
#     # Создаем токен для подтверждения email
#     token = str(uuid.uuid4())  # Генерация случайного токена для теста
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#
#     confirmation_url = reverse('confirm_email', kwargs={'token': token})
#     email = render_to_string('registration/confirmation_email.html', {
#         'user': user,
#         'domain': get_current_site(client).domain,
#         'uid': uid,
#         'token': token
#     })
#
#     # Отправка подтверждения
#     response = client.get(confirmation_url)
#
#     # Проверка, что запрос на подтверждение email прошел успешно
#     assert response.status_code == status.HTTP_200_OK
#     assert "Ваш email успешно подтвержден!" in response.data["message"]
#
#     # Проверка, что пользователь активирован
#     user.refresh_from_db()
#     assert user.is_active

# Тесты для проверки работы логина

# import pytest
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from rest_framework.authtoken.models import Token
# from rest_framework.test import APIClient
#
#
# @pytest.fixture
# def user():
#     """Фикстура для создания тестового пользователя"""
#     return get_user_model().objects.create_user(
#         email="testuser@example.com",
#         password="testpassword123",
#         first_name="Test",
#         last_name="User",
#         company="TestCompany",
#         position="TestPosition"
#     )
#
#
# @pytest.fixture
# def api_client():
#     """Фикстура для создания клиента API"""
#     return APIClient()
#
#
# def test_successful_login(api_client, user):
#     """Проверка успешного логина с правильными учетными данными"""
#     url = '/api/login/'  # Укажите свой путь
#     data = {
#         "email": user.email,
#         "password": "testpassword123"
#     }
#     response = api_client.post(url, data, format='json')
#
#     assert response.status_code == status.HTTP_200_OK
#     assert 'token' in response.data  # Проверяем наличие токена в ответе
#
#
# def test_invalid_credentials(api_client):
#     """Проверка логина с неверным email или паролем"""
#     url = '/api/login/'
#     data = {
#         "email": "wronguser@example.com",  # Неверный email
#         "password": "wrongpassword"
#     }
#     response = api_client.post(url, data, format='json')
#
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.data == {"detail": "Неверные учетные данные."}
#
#
# def test_inactive_user_login(api_client, user):
#     """Проверка логина для неактивного пользователя"""
#     user.is_active = False
#     user.save()
#
#     url = '/api/login/'
#     data = {
#         "email": user.email,
#         "password": "testpassword123"
#     }
#     response = api_client.post(url, data, format='json')
#
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.data == {"detail": "Ваш аккаунт не активен. Пожалуйста, обратитесь к администратору."}
#
#
# def test_missing_email_or_password(api_client):
#     """Проверка на отсутствие email или пароля в запросе"""
#     url = '/api/login/'
#
#     # Отсутствует email
#     data = {"password": "testpassword123"}
#     response = api_client.post(url, data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#     # Отсутствует password
#     data = {"email": "testuser@example.com"}
#     response = api_client.post(url, data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST

# Тесты для проверки функционала добавления контактов

# import pytest
# from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token
# from backend.models import User, Contact
#
#
# @pytest.fixture
# def api_client():
#     return APIClient()
#
#
# @pytest.fixture
# def user():
#     user = User.objects.create_user(
#         email="testuser@example.com",
#         password="strongpassword",
#         first_name="Test",
#         last_name="User"
#     )
#     return user
#
#
# @pytest.fixture
# def auth_client(api_client, user):
#     token, _ = Token.objects.get_or_create(user=user)
#     api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
#     return api_client
#
#
# @pytest.mark.django_db
# def test_add_contact(auth_client, user):
#     url = "/api/contacts/"
#     data = {
#         "city": "Москва",
#         "street": "Тверская",
#         "house": "12",
#         "apartment": "25",
#         "phone": "+79991234567"
#     }
#
#     response = auth_client.post(url, data)
#
#     assert response.status_code == 201
#     response_data = response.json()
#     assert response_data["city"] == "Москва"
#     assert response_data["street"] == "Тверская"
#     assert response_data["house"] == "12"
#     assert response_data["apartment"] == "25"
#     assert response_data["phone"] == "+79991234567"
#
#     # Проверяем, что контакт привязан к пользователю
#     contact = Contact.objects.get(id=response_data["id"])
#     assert contact.user == user
#
#
# @pytest.mark.django_db
# def test_add_contact_unauthenticated(api_client):
#     url = "/api/contacts/"
#     data = {
#         "city": "Москва",
#         "street": "Тверская",
#         "house": "12",
#         "apartment": "25",
#         "phone": "+79991234567"
#     }
#
#     response = api_client.post(url, data)
#
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication credentials were not provided."
#
#
# @pytest.mark.django_db
# def test_get_contacts(auth_client, user):
#     Contact.objects.create(
#         city="Москва",
#         street="Тверская",
#         house="12",
#         apartment="25",
#         phone="+79991234567"
#     )
#
#     url = "/api/contacts/"
#     response = auth_client.get(url)
#
#     assert response.status_code == 200
#     response_data = response.json()
#     assert len(response_data) == 1
#     assert response_data[0]["city"] == "Москва"
#     assert response_data[0]["street"] == "Тверская"
#     assert response_data[0]["house"] == "12"
#     assert response_data[0]["apartment"] == "25"
#     assert response_data[0]["phone"] == "+79991234567"

# Тест для получения данных контактов

# @pytest.mark.django_db
# def test_get_contacts_authenticated(auth_client, user):
#     # Создаем тестовый контакт
#     Contact.objects.create(
#         city="Москва",
#         street="Тверская",
#         house="12",
#         apartment="25",
#         phone="+79991234567"
#     )
#
#     # Отправляем запрос
#     url = "/api/contacts/"
#     response = auth_client.get(url)
#
#     # Проверяем успешность ответа
#     assert response.status_code == 200
#     response_data = response.json()
#
#     # Проверяем данные контакта
#     assert len(response_data) == 1
#     assert response_data[0]["city"] == "Москва"
#     assert response_data[0]["street"] == "Тверская"
#     assert response_data[0]["house"] == "12"
#     assert response_data[0]["apartment"] == "25"
#     assert response_data[0]["phone"] == "+79991234567"
#
#
# @pytest.mark.django_db
# def test_get_contacts_unauthenticated(api_client):
#     url = "/api/contacts/"
#     response = api_client.get(url)
#
#     # Проверяем статус неавторизованного запроса
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication credentials were not provided."

# Тест на изменение информации контакта

# @pytest.mark.django_db
# def test_update_contact_authenticated(auth_client, user):
#     # Создаем тестовый контакт
#     contact = Contact.objects.create(
#         city="Москва",
#         street="Тверская",
#         house="12",
#         apartment="25",
#         phone="+79991234567"
#     )
#
#     # Данные для обновления
#     updated_data = {
#         "city": "Санкт-Петербург",
#         "street": "Невский проспект",
#         "house": "25",
#         "apartment": "45",
#         "phone": "+79990001122"
#     }
#
#     # Отправляем PUT-запрос
#     url = f"/api/contacts/{contact.id}/"
#     response = auth_client.put(url, data=updated_data, format="json")
#
#     # Проверяем успешность ответа
#     assert response.status_code == 200
#     response_data = response.json()
#
#     # Проверяем, что данные обновлены
#     assert response_data["city"] == "Санкт-Петербург"
#     assert response_data["street"] == "Невский проспект"
#     assert response_data["house"] == "25"
#     assert response_data["apartment"] == "45"
#     assert response_data["phone"] == "+79990001122"
#
#
# @pytest.mark.django_db
# def test_update_contact_unauthenticated(api_client):
#     # Попытка обновить контакт без авторизации
#     url = "/api/contacts/1/"
#     updated_data = {
#         "city": "Санкт-Петербург",
#         "street": "Невский проспект",
#         "house": "25",
#         "apartment": "45",
#         "phone": "+79990001122"
#     }
#     response = api_client.put(url, data=updated_data, format="json")
#
#     # Проверяем статус неавторизованного запроса
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication credentials were not provided."
#
#
# @pytest.mark.django_db
# def test_update_contact_not_found(auth_client):
#     # Попытка обновить несуществующий контакт
#     url = "/api/contacts/999/"
#     updated_data = {
#         "city": "Санкт-Петербург",
#         "street": "Невский проспект",
#         "house": "25",
#         "apartment": "45",
#         "phone": "+79990001122"
#     }
#     response = auth_client.put(url, data=updated_data, format="json")
#
#     # Проверяем статус ошибки "Не найдено"
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Not found."

# Тест на удаление контакта

# import pytest
# from rest_framework.test import APIClient
# from backend.models import Contact, User
#
# @pytest.mark.django_db
# def test_delete_contact_authenticated(auth_client, user):
#     # Создаем тестовый контакт
#     contact = Contact.objects.create(
#         city="Москва",
#         street="Тверская",
#         house="12",
#         apartment="25",
#         phone="+79991234567"
#     )
#
#     # Удаляем контакт
#     url = f"/api/contacts/{contact.id}/"
#     response = auth_client.delete(url)
#
#     # Проверяем статус успешного удаления
#     assert response.status_code == 204
#
#     # Проверяем, что контакт удален из базы
#     assert not Contact.objects.filter(id=contact.id).exists()
#
#
# @pytest.mark.django_db
# def test_delete_contact_unauthenticated(api_client):
#     # Создаем тестового пользователя и контакт
#     user = User.objects.create_user(email="user@example.com", password="password123")
#     contact = Contact.objects.create(
#         city="Москва",
#         street="Тверская",
#         house="12",
#         apartment="25",
#         phone="+79991234567"
#     )
#
#     # Пытаемся удалить контакт без авторизации
#     url = f"/api/contacts/{contact.id}/"
#     response = api_client.delete(url)
#
#     # Проверяем, что запрос без авторизации возвращает 401
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication credentials were not provided."
#
#
# @pytest.mark.django_db
# def test_delete_contact_not_found(auth_client):
#     # Пытаемся удалить несуществующий контакт
#     url = "/api/contacts/999/"
#     response = auth_client.delete(url)
#
#     # Проверяем, что запрос возвращает 404
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Not found."

# Тест на получение информации о юзере / пользователе

# import pytest
# from rest_framework.test import APIClient
# from backend.models import User
#
#
# @pytest.fixture
# def user(db):
#     return User.objects.create_user(
#         email="a.legkovsky@gmail.com",
#         password="securepassword",
#         first_name="Алексей",
#         last_name="Легковский"
#     )
#
#
# @pytest.fixture
# def auth_client(user):
#     client = APIClient()
#     client.force_authenticate(user=user)
#     return client
#
#
# @pytest.fixture
# def api_client():
#     return APIClient()
#
#
# @pytest.mark.django_db
# def test_get_user_authenticated(auth_client, user):
#     url = "/api/user/"
#     response = auth_client.get(url)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == user.id
#     assert data["email"] == user.email
#     assert data["first_name"] == user.first_name
#     assert data["last_name"] == user.last_name
#
#
# @pytest.mark.django_db
# def test_get_user_unauthenticated(api_client):
#     url = "/api/user/"
#     response = api_client.get(url)
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication credentials were not provided."

# Тест на обновление информации о юзере / пользователе

# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import User
#
#
# class UserUpdateTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email='testuser@example.com',
#             password='testpassword',
#             first_name='Test',
#             last_name='User'
#         )
#         self.client.login(username=self.user.email, password='testpassword')  # Аутентификация
#
#     def test_update_user(self):
#         url = '/api/user/update/'
#         data = {
#             "email": "updateduser@example.com",
#             "password": "newpassword",
#             "first_name": "Updated",
#             "last_name": "UserUpdated"
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # Проверяем обновление данных
#         self.user.refresh_from_db()
#         self.assertEqual(self.user.email, "updateduser@example.com")
#         self.assertEqual(self.user.first_name, "Updated")
#         self.assertEqual(self.user.last_name, "UserUpdated")
#
#     def test_partial_update_user(self):
#         url = '/api/user/update/'
#         data = {
#             "first_name": "PartiallyUpdated"
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # Проверяем обновление только имени
#         self.user.refresh_from_db()
#         self.assertEqual(self.user.first_name, "PartiallyUpdated")
#         self.assertEqual(self.user.last_name, "User")  # Остальные данные не изменились

# Тесты на сброс пароля

# import pytest
# from django.contrib.auth.models import User
# from django.contrib.auth.tokens import default_token_generator
# from rest_framework.test import APIClient
# from rest_framework import status
#
#
# @pytest.fixture
# def create_user(db):
#     """Фикстура для создания пользователя."""
#     return User.objects.create_user(
#         email="testuser@example.com",
#         password="securepassword"
#     )
#
#
# @pytest.fixture
# def client():
#     """Фикстура для создания клиента API."""
#     return APIClient()
#
#
# @pytest.fixture
# def reset_token(create_user):
#     """Фикстура для создания токена сброса пароля."""
#     return default_token_generator.make_token(create_user)
#
#
# @pytest.mark.django_db
# def test_password_reset_confirm_success(client, create_user, reset_token):
#     """Тест успешного подтверждения сброса пароля."""
#     url = "/api/password-reset-confirm/"
#     data = {
#         "email": create_user.email,
#         "password": "newsecurepassword",
#         "token": reset_token,
#     }
#
#     response = client.post(url, data)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["detail"] == "Пароль успешно изменён."
#
#     # Проверяем, что новый пароль работает
#     login_successful = client.login(username=create_user.email, password="newsecurepassword")
#     assert login_successful
#
#
# @pytest.mark.django_db
# def test_password_reset_confirm_invalid_token(client, create_user):
#     """Тест подтверждения сброса пароля с неверным токеном."""
#     url = "/api/password-reset-confirm/"
#     data = {
#         "email": create_user.email,
#         "password": "newsecurepassword",
#         "token": "invalid-token",
#     }
#
#     response = client.post(url, data)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["detail"] == "Токен недействителен или истек."
#
#
# @pytest.mark.django_db
# def test_password_reset_confirm_user_not_found(client, reset_token):
#     """Тест подтверждения сброса пароля для несуществующего пользователя."""
#     url = "/api/password-reset-confirm/"
#     data = {
#         "email": "nonexistent@example.com",
#         "password": "newsecurepassword",
#         "token": reset_token,
#     }
#
#     response = client.post(url, data)
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.data["detail"] == "Пользователь с таким email не найден."
#
#
# @pytest.mark.django_db
# def test_password_reset_confirm_missing_data(client):
#     """Тест подтверждения сброса пароля с отсутствующими данными."""
#     url = "/api/password-reset-confirm/"
#     data = {
#         "email": "testuser@example.com",
#     }
#
#     response = client.post(url, data)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["detail"] == "Необходимо указать email, password и token."

# Тест для проверки импорта данных из shop.yaml

# import pytest
# from unittest.mock import patch, mock_open
# from rest_framework.test import APIClient
# from rest_framework.reverse import reverse
# from rest_framework import status
# from backend.models import Shop, Category, Product
#
#
# @pytest.mark.django_db
# def test_import_products_successful():
#     client = APIClient()
#
#     # Тестовые данные в формате YAML
#     shop_yaml_content = """
#     categories:
#       - id: 1
#         name: Категория 1
#       - id: 2
#         name: Категория 2
#     goods:
#       - id: 1001
#         category: 1
#         model: Модель 1
#         name: Товар 1
#         price: 1000
#         price_rrc: 1200
#         quantity: 5
#         parameters:
#           "Параметр 1": "Значение 1"
#       - id: 1002
#         category: 2
#         model: Модель 2
#         name: Товар 2
#         price: 2000
#         price_rrc: 2400
#         quantity: 3
#         parameters:
#           "Параметр 2": "Значение 2"
#     """
#
#     # Мокаем open для чтения тестового YAML
#     with patch("builtins.open", mock_open(read_data=shop_yaml_content)):
#         url = reverse('import_products')  # Имя URL из urls.py
#         response = client.post(url, {}, format='json')  # Пустой запрос, так как данные берутся из файла
#
#         # Проверяем успешность импорта
#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.json() == {"message": "Products imported successfully"}
#
#         # Проверяем, что категории были созданы
#         shop_1 = Shop.objects.get(id=1)  # Проверяем, что магазин с id=1 был создан
#         category_1 = Category.objects.get(shop_id=shop_1, name="Категория 1")
#         assert category_1.name == "Категория 1"
#
#         shop_2 = Shop.objects.get(id=2)  # Проверяем, что магазин с id=2 был создан
#         category_2 = Category.objects.get(shop_id=shop_2, name="Категория 2")
#         assert category_2.name == "Категория 2"
#
#         # Проверяем, что товары были созданы и привязаны к соответствующим категориям
#         # Используем name товара, чтобы избежать зависимости от id
#         product_1 = Product.objects.get(name="Товар 1")
#         assert product_1.model == "Модель 1"
#         assert product_1.name == "Товар 1"
#         assert product_1.price == 1000
#         assert product_1.price_rrc == 1200
#         assert product_1.quantity == 5
#         assert product_1.parameters == {"Параметр 1": "Значение 1"}
#         assert product_1.category == category_1
#
#         product_2 = Product.objects.get(name="Товар 2")
#         assert product_2.model == "Модель 2"
#         assert product_2.name == "Товар 2"
#         assert product_2.price == 2000
#         assert product_2.price_rrc == 2400
#         assert product_2.quantity == 3
#         assert product_2.parameters == {"Параметр 2": "Значение 2"}
#         assert product_2.category == category_2
