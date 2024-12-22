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
#         user=user,
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
