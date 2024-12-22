from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Cart, Contact, Order, OrderItem


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'username']

    def validate_email(self, value):
        """Проверка уникальности email"""
        if User.objects.filter(email=value).exists():
            raise ValidationError("Этот email уже занят.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')  # Извлекаем пароль

        # Если username не предоставлен, создаем его из email
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email']

        user = User.objects.create_user(**validated_data)  # Создаем пользователя с переданными данными
        user.set_password(password)  # Устанавливаем безопасный пароль
        user.save()  # Сохраняем пользователя
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        return user


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        # Дополнительная валидация, если нужно
        return value


class ShopSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(child=serializers.DictField())
    goods = serializers.ListField(child=serializers.DictField())

    class Meta:
        model = Shop
        fields = ['name', 'url', 'categories', 'goods']

    def create(self, validated_data):
        shop_data = validated_data.pop('shop')
        categories_data = validated_data.pop('categories')
        goods_data = validated_data.pop('goods')

        shop = Shop.objects.create(name=shop_data['name'], url=shop_data['url'])

        for category in categories_data:
            category_obj = Category.objects.create(name=category['name'])

        for good in goods_data:
            product = Product.objects.create(
                category=category_obj,
                name=good['name'],
                price=good['price'],
                price_rrc=good['price_rrc'],
                quantity=good['quantity']
            )
            ProductInfo.objects.create(
                product=product,
                shop=shop,
                quantity=good['quantity'],
                price=good['price'],
                price_rrc=good['price_rrc']
            )

        return shop


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ['name', 'category']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())

    class Meta:
        model = ProductInfo
        fields = ['product', 'shop', 'quantity', 'price', 'price_rrc']


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name']


class ProductParameterSerializer(serializers.ModelSerializer):
    product_info = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.all())
    parameter = serializers.PrimaryKeyRelatedField(queryset=Parameter.objects.all())

    class Meta:
        model = ProductParameter
        fields = ['product_info', 'parameter', 'value']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'price_rrc']


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    quantity = serializers.IntegerField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'user', 'city', 'street', 'house', 'apartment', 'phone']


class OrderConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = 'confirmed'
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'shop']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'updated_at', 'items']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(Order.STATUS_CHOICES):
            raise serializers.ValidationError("Некорректный статус.")
        return value


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['product', 'shop', 'quantity', 'price', 'price_rrc']
