import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import now
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Product, Cart, Contact, Order, ProductInfo, EmailConfirmation, Category, Shop
from .serializers import UserRegisterSerializer, LoginSerializer, ShopSerializer, CategorySerializer, ProductSerializer, \
    ProductInfoSerializer, ProductListSerializer, CartSerializer, ContactSerializer, OrderConfirmationSerializer, \
    OrderSerializer, OrderStatusUpdateSerializer, ProductDetailSerializer, UserSerializer
from django.core.exceptions import ValidationError
import yaml
from django.core.mail import send_mail
from django.conf import settings


# class RegisterUserView(APIView):
#     permission_classes = [permissions.AllowAny]
#
#     def post(self, request):
#         serializer = UserRegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"Сообщение": "Пользователь успешно зарегистрирован!"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Генерация токена для подтверждения
            token = uuid.uuid4()
            EmailConfirmation.objects.create(user=user, token=token)

            # Формирование ссылки
            confirmation_url = f"{settings.FRONTEND_URL}{reverse('confirm_email', kwargs={'token': token})}"

            # Отправка письма
            subject = "Подтверждение электронной почты"
            message = f"Для подтверждения регистрации перейдите по ссылке: {confirmation_url}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return Response(
                {"message": "Пользователь успешно зарегистрирован! Проверьте свою почту для подтверждения."},
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    def get(self, request, token):
        try:
            confirmation = EmailConfirmation.objects.get(token=token)
            user = confirmation.user
            user.is_active = True
            user.save()
            confirmation.delete()  # Удаляем токен после подтверждения
            return Response({"message": "Электронная почта успешно подтверждена!"}, status=status.HTTP_200_OK)
        except EmailConfirmation.DoesNotExist:
            return Response({"error": "Неверный или устаревший токен."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)

        if user is None:
            return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем или создаем токен для пользователя
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Только для аутентифицированных пользователей

    def post(self, request):
        user = request.user  # Текущий пользователь
        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь с таким email не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Генерация токена сброса пароля
        token = default_token_generator.make_token(user)
        reset_link = f"http://example.com/password-reset-confirm/{user.pk}/{token}/"  # Ссылка для подтверждения

        # Отправка email
        send_mail(
            subject="Сброс пароля",
            message=f"Ваш токен сброса пароля: {reset_link}",
            from_email="no-reply@example.com",
            recipient_list=[user.email],
        )
        return Response({"detail": "Инструкции по сбросу пароля отправлены на email."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        token = request.data.get('token')

        if not email or not password or not token:
            return Response({"detail": "Необходимо указать email, password и token."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь с таким email не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Проверка токена
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Токен недействителен или истек."}, status=status.HTTP_400_BAD_REQUEST)

        # Установка нового пароля
        user.set_password(password)
        user.save()
        return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)


class ImportProductsView(APIView):
    def post(self, request):
        try:
            with open('data/shop.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

            # Импортируем категории
            categories = data.get('categories', [])
            for category_data in categories:
                try:
                    # Получаем или создаем объект Shop
                    shop, created = Shop.objects.get_or_create(id=category_data['id'])

                    # Создаем категорию, используя поле shop_id
                    category, created = Category.objects.get_or_create(
                        shop_id=shop,  # Используем shop_id, так как в модели именно это поле
                        name=category_data['name']
                    )

                except Exception as e:
                    return Response({"error": f"Error creating category: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Импортируем товары
            products = data.get('goods', [])
            for product_data in products:
                try:
                    # Находим категорию по shop_id, используя filter(), чтобы избежать множественных результатов
                    categories = Category.objects.filter(shop_id=product_data['category'])

                    if categories.exists():
                        category = categories.first()  # Получаем первую категорию
                    else:
                        return Response({"error": f"Category with shop_id {product_data['category']} does not exist."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    # Создаем товар
                    product = Product(
                        category=category,
                        model=product_data['model'],
                        name=product_data['name'],
                        price=product_data['price'],
                        price_rrc=product_data['price_rrc'],
                        quantity=product_data['quantity'],
                        parameters=product_data['parameters']
                    )
                    product.save()

                except Exception as e:
                    return Response({"error": f"Error creating product: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Products imported successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"An error occurred during the import: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)


class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class CartView(APIView):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        product = Product.objects.get(id=product_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({'status': 'added'})

    def delete(self, request):
        product_id = request.data.get('product_id')
        Cart.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({'status': 'removed'})


class ContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, contact_id, user):
        try:
            return Contact.objects.get(id=contact_id, user=user)
        except Contact.DoesNotExist:
            return None

    def get(self, request, contact_id):
        contact = self.get_object(contact_id, request.user)
        if contact is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    def put(self, request, contact_id):
        contact = self.get_object(contact_id, request.user)
        if contact is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, contact_id):
        contact = self.get_object(contact_id, request.user)
        if contact is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderConfirmationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderConfirmationSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, order_id, user):
        try:
            return Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return None

    def get(self, request, order_id):
        order = self.get_object(order_id, request.user)
        if order is None:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            order = serializer.save()
            # Отправляем email, если заказ подтвержден
            if order.status == "confirmed":
                send_confirmation_email(order.user.email, order.id)
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get(self, request, id):  # Используем id, так как в URL мы передаем id
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"detail": "Продукт не найден."}, status=status.HTTP_404_NOT_FOUND)


def send_confirmation_email(user_email, order_id):
    subject = 'Подтверждение заказа'
    message = f'Ваш заказ #{order_id} был подтвержден. Спасибо за покупку!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
