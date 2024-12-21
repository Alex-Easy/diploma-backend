import yaml
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer, ProductInfoSerializer
from .models import Shop, Category, Product, ProductInfo


class ProductImportAPIView(APIView):
    def post(self, request, *args, **kwargs):
        print(f"Request data: {request.data}")

        # Проверка авторизации пользователя
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Пользователь не авторизован'}, status=status.HTTP_403_FORBIDDEN)

        # Получение и проверка файла
        file = request.FILES.get('file')
        if file is None:
            return Response({'Status': False, 'Error': 'Нет загруженного файла'}, status=status.HTTP_400_BAD_REQUEST)

        # Парсинг YAML файла
        try:
            data = yaml.safe_load(file.read())
        except yaml.YAMLError as e:
            return Response({'Status': False, 'Error': f'Ошибка при разборе файла YAML: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Валидация данных магазина
        shop_data = {'name': data['shop']}
        shop_serializer = ShopSerializer(data=shop_data)
        if not shop_serializer.is_valid():
            return Response({'Status': False, 'Error': shop_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        shop = shop_serializer.save()

        # Валидация и сохранение категорий
        for category_data in data['categories']:
            category_serializer = CategorySerializer(data=category_data)
            if not category_serializer.is_valid():
                return Response({'Status': False, 'Error': category_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            category_serializer.save()

        # Валидация и сохранение товаров
        for product_data in data['goods']:
            product_serializer = ProductSerializer(data=product_data)
            if not product_serializer.is_valid():
                return Response({'Status': False, 'Error': product_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            product = product_serializer.save()

            # Сохранение информации о товаре
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

        # Ответ об успешном импорте
        return Response({'Status': True, 'Message': 'Товары успешно импортированы'}, status=status.HTTP_201_CREATED)
