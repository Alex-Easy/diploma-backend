from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Product, Cart, Contact, Order
from .serializers import UserRegisterSerializer, LoginSerializer, ShopSerializer, CategorySerializer, ProductSerializer, \
    ProductInfoSerializer, ProductListSerializer, CartSerializer, ContactSerializer, OrderConfirmationSerializer
from django.core.exceptions import ValidationError
import yaml


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Сообщение": "Пользователь успешно зарегистрирован!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({"токен": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImportProductsView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Пользователь не авторизован'}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('file')
        if file is None:
            return Response({'Status': False, 'Error': 'Нет загруженного файла'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = yaml.safe_load(file.read())
        except yaml.YAMLError as e:
            return Response({'Status': False, 'Error': f'Ошибка при разборе файла YAML: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Валидация и импорт данных магазина
        shop_data = {'name': data['shop']}
        shop_serializer = ShopSerializer(data=shop_data)
        if not shop_serializer.is_valid():
            return Response({'Status': False, 'Error': shop_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        shop = shop_serializer.save()

        # Валидация и импорт категорий
        for category_data in data['categories']:
            category_serializer = CategorySerializer(data=category_data)
            if not category_serializer.is_valid():
                return Response({'Status': False, 'Error': category_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            category_serializer.save()

        # Валидация и импорт продуктов
        for product_data in data['goods']:
            product_serializer = ProductSerializer(data=product_data)
            if not product_serializer.is_valid():
                return Response({'Status': False, 'Error': product_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            product = product_serializer.save()

            product_info_data = {
                'product': product.id,
                'shop': shop.id,
                'quantity': product_data['quantity'],
                'price': product_data['price'],
                'price_rrc': product_data['price_rrc']
            }
            product_info_serializer = ProductInfoSerializer(data=product_info_data)
            if not product_info_serializer.is_valid():
                return Response({'Status': False, 'Error': product_info_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            product_info_serializer.save()

        return Response({'Status': True, 'Message': 'Товары успешно импортированы'}, status=status.HTTP_201_CREATED)


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
