from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError


# TODO: think about how to add user model


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
    CONTACT_TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Телефон'),
        ('address', 'Адрес'),
    ]
    type = models.CharField(max_length=50, choices=CONTACT_TYPE_CHOICES, verbose_name='Тип контакта',
                            help_text='Тип контакта')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts',
                             verbose_name='Пользователь', help_text='Пользователь, который представлен в контакте')
    value = models.CharField(max_length=255, verbose_name='Значение контакта', help_text='Значение контакта')

    def clean(self):
        value = str(self.value)
        if self.type == 'email':
            EmailValidator(message="Введите корректный email-адрес.")(value)
        elif self.type == 'phone':
            RegexValidator(regex=r'^\+?\d{10,15}$', message="Введите корректный номер телефона.")(value)
        elif self.type == 'address':
            synonyms = {
                'город': ['г.', 'г', 'город'],
                'улица': ['ул.', 'ул', 'улица'],
                'дом': ['д.', 'д', 'дом'],
            }

            value_lower = value.lower()

            for standard_word, variants in synonyms.items():
                for variant in variants:
                    value_lower = value_lower.replace(variant, standard_word)

            required_words = ['город', 'улица', 'дом']

            for word in required_words:
                if word not in value_lower:
                    raise ValidationError(
                        f"Адрес должен содержать следующие элементы: '{', '.join(required_words)}'."
                    )


