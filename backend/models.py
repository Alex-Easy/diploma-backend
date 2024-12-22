import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Электронная почта",
                              help_text="Уникальный адрес электронной почты")
    first_name = models.CharField(max_length=255, verbose_name="Имя", help_text="Имя пользователя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия", help_text="Фамилия пользователя")
    company = models.CharField(max_length=255, verbose_name="Компания", help_text="Компания пользователя")
    position = models.CharField(max_length=255, verbose_name="Должность", help_text="Должность пользователя")

    username = models.CharField(max_length=255, unique=True, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(Group, related_name='backend_user_groups', blank=True,
                                    verbose_name="Группы", help_text="Группы, к которым принадлежит пользователь")
    user_permissions = models.ManyToManyField(Permission, related_name='backend_user_permissions', blank=True,
                                              verbose_name="Права пользователя",
                                              help_text="Права доступа, назначенные пользователю")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Shop(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название магазина',
                            help_text='Уникальное название магазина')
    url = models.URLField(verbose_name='URL магазина', help_text='Адрес магазина в интернете')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название категории',
                            help_text='Уникальное название категории')
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазины',
                                   help_text='Магазины, в которых представлена данная категория')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория',
                                 help_text='Категория продукта')
    name = models.CharField(max_length=255, unique=True, verbose_name='Название продукта',
                            help_text='Уникальное название продукта')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        indexes = [
            models.Index(fields=['name'], name='product_name_idx'),
        ]


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='info', verbose_name='Продукт',
                                help_text='Продукт, который представлен в магазине')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos', verbose_name='Магазин',
                             help_text='Магазин, в котором представлен продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество', help_text='Количество продукта в магазине')
    price = models.PositiveIntegerField(verbose_name='Цена', help_text='Цена продукта в магазине в рублях')
    price_rrc = models.PositiveIntegerField(verbose_name='Цена розничная',
                                            help_text='Розничная цена продукта в магазине')

    def clean(self):
        if self.price_rrc < self.price:
            raise ValidationError('Розничная цена (price_rrc) не может быть ниже обычной цены (price).')

    def __str__(self):
        return f'{self.product.name} - {self.shop.name}'

    class Meta:
        unique_together = ('product', 'shop')
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'


class Parameter(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название параметра',
                            help_text='Уникальное название параметра')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='parameters',
                                     verbose_name='Информация о продукте', help_text='Продукт в магазине')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters',
                                  verbose_name='Параметр', help_text='Параметр продукта в магазине')
    value = models.CharField(max_length=255, verbose_name='Значение параметра', help_text='Значение параметра продукта')

    def __str__(self):
        return f'{self.product_info.product.name} - {self.parameter.name}'

    class Meta:
        unique_together = ('product_info', 'parameter')
        verbose_name = 'Параметр продукта'
        verbose_name_plural = 'Параметры продукта'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В процессе'),
        ('confirmed', 'Подтверждён'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
                             verbose_name='Пользователь', help_text='Пользователь, который сделал заказ')
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время заказа', help_text='Дата и время заказа')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True,
                              verbose_name='Статус заказа', help_text='Статус заказа')

    def __str__(self):
        return f'Заказ #{self.id} ({self.dt:%Y-%m-%d %H:%M:%S})'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ',
                              help_text='Заказ, в котором представлен продукт')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='Продукт',
                                help_text='Продукт, который представлен в заказе')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='order_items', verbose_name='Магазин',
                             help_text='Магазин, в котором представлен продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество', help_text='Количество продукта в заказе')

    def __str__(self):
        return f'{self.product.name} x {self.quantity} (заказ #{self.order.id})'

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'


class Contact(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="contacts", on_delete=models.CASCADE,
                             verbose_name="Пользователь",
                             help_text="Пользователь, для которого указан контакт")
    city = models.CharField(max_length=255, verbose_name="Город", help_text="Город проживания пользователя")
    street = models.CharField(max_length=255, verbose_name="Улица", help_text="Улица проживания пользователя")
    house = models.CharField(max_length=255, verbose_name="Дом", help_text="Номер дома")
    apartment = models.CharField(max_length=255, verbose_name="Квартира", help_text="Номер квартиры")
    phone = models.CharField(max_length=15, verbose_name="Телефон", help_text="Контактный телефон пользователя")

    def __str__(self):
        return f'{self.city}, {self.street}, {self.phone}'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"Cart item for {self.user} - {self.product.name}"


User = get_user_model()


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_confirmation")
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Токен подтверждения для {self.user.email}"
