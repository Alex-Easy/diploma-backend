import yaml
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shop, Category, Product, ProductInfo


class ProductImportAPIView(APIView):
    def post(self, request, *args, **kwargs):
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

        shop_data = data['shop']
        shop, _ = Shop.objects.get_or_create(name=shop_data)

        for category_data in data['categories']:
            category, _ = Category.objects.get_or_create(id=category_data['id'], name=category_data['name'])

        for product_data in data['goods']:
            try:
                category = Category.objects.get(id=product_data['category'])
            except Category.DoesNotExist:
                return Response({'Status': False, 'Error': f"Категория с id {product_data['category']} не найдена"},
                                status=status.HTTP_400_BAD_REQUEST)

            product, _ = Product.objects.get_or_create(
                name=product_data['name'],
                category=category,
                model=product_data['model'],
                price=product_data['price'],
                price_rrc=product_data['price_rrc'],
                quantity=product_data['quantity']
            )

            ProductInfo.objects.create(
                product=product,
                shop=shop,
                quantity=product_data['quantity'],
                price=product_data['price'],
                price_rrc=product_data['price_rrc']
            )

        return Response({'Status': True, 'Message': 'Товары успешно импортированы'}, status=status.HTTP_201_CREATED)
