# Generated by Django 5.1.4 on 2024-12-16 14:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Уникальное название категории', max_length=255, unique=True, verbose_name='Название категории')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Уникальное название параметра', max_length=255, unique=True, verbose_name='Название параметра')),
            ],
            options={
                'verbose_name': 'Параметр',
                'verbose_name_plural': 'Параметры',
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Уникальное название магазина', max_length=255, unique=True, verbose_name='Название магазина')),
                ('url', models.URLField(help_text='Адрес магазина в интернете', verbose_name='URL магазина')),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField(auto_now_add=True, help_text='Дата и время заказа', verbose_name='Дата и время заказа')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('processing', 'В процессе'), ('delivered', 'Доставлен'), ('cancelled', 'Отменён')], db_index=True, default='new', help_text='Статус заказа', max_length=20, verbose_name='Статус заказа')),
                ('user', models.ForeignKey(help_text='Пользователь, который сделал заказ', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Уникальное название продукта', max_length=255, unique=True, verbose_name='Название продукта')),
                ('category', models.ForeignKey(help_text='Категория продукта', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='backend.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
            },
        ),
        migrations.CreateModel(
            name='ProductInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='Количество продукта в магазине', verbose_name='Количество')),
                ('price', models.PositiveIntegerField(help_text='Цена продукта в магазине в рублях', verbose_name='Цена')),
                ('price_rrc', models.PositiveIntegerField(help_text='Розничная цена продукта в магазине', verbose_name='Цена розничная')),
                ('product', models.ForeignKey(help_text='Продукт, который представлен в магазине', on_delete=django.db.models.deletion.CASCADE, related_name='info', to='backend.product', verbose_name='Продукт')),
                ('shop', models.ForeignKey(help_text='Магазин, в котором представлен продукт', on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='backend.shop', verbose_name='Магазин')),
            ],
            options={
                'verbose_name': 'Информация о продукте',
                'verbose_name_plural': 'Информация о продуктах',
            },
        ),
        migrations.CreateModel(
            name='ProductParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(help_text='Значение параметра продукта', max_length=255, verbose_name='Значение параметра')),
                ('parameter', models.ForeignKey(help_text='Параметр продукта в магазине', on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='backend.parameter', verbose_name='Параметр')),
                ('product_info', models.ForeignKey(help_text='Продукт в магазине', on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='backend.productinfo', verbose_name='Информация о продукте')),
            ],
            options={
                'verbose_name': 'Параметр продукта',
                'verbose_name_plural': 'Параметры продукта',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='Количество продукта в заказе', verbose_name='Количество')),
                ('order', models.ForeignKey(help_text='Заказ, в котором представлен продукт', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='backend.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(help_text='Продукт, который представлен в заказе', on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='backend.product', verbose_name='Продукт')),
                ('shop', models.ForeignKey(help_text='Магазин, в котором представлен продукт', on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='backend.shop', verbose_name='Магазин')),
            ],
            options={
                'verbose_name': 'Элемент заказа',
                'verbose_name_plural': 'Элементы заказа',
            },
        ),
        migrations.AddField(
            model_name='category',
            name='shops',
            field=models.ManyToManyField(help_text='Магазины, в которых представлена данная категория', related_name='categories', to='backend.shop', verbose_name='Магазины'),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('email', 'Email'), ('phone', 'Телефон'), ('address', 'Адрес')], help_text='Тип контакта', max_length=50, verbose_name='Тип контакта')),
                ('value', models.CharField(help_text='Значение контакта', max_length=255, verbose_name='Значение контакта')),
                ('user', models.ForeignKey(help_text='Пользователь, который представлен в контакте', on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Контакт',
                'verbose_name_plural': 'Контакты',
                'unique_together': {('user', 'type', 'value')},
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='product_name_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='productparameter',
            unique_together={('product_info', 'parameter')},
        ),
        migrations.AlterUniqueTogether(
            name='productinfo',
            unique_together={('product', 'shop')},
        ),
    ]