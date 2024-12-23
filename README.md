# Дипломный проект профессии «Python-разработчик: расширенный курс»

## Backend-приложение для автоматизации закупок

### Цель дипломного проекта

Создадите и настроите проект по автоматизации закупок в розничной сети, проработаете модели данных, импорт товаров, API views.

### Общее описание приложения

Приложение предназначено для автоматизации закупок в розничной сети через REST API.


**Пользователи сервиса:**

1. Клиент (покупатель):

- делает ежедневные закупки по каталогу, в котором представлены товары от нескольких поставщиков,
- в одном заказе можно указать товары от разных поставщиков,
- пользователь может авторизироваться, регистрироваться и восстанавливать пароль через API.
    
2. Поставщик:

- через API информирует сервис об обновлении прайса,
- может включать и отключать приём заказов,
- может получать список оформленных заказов (с товарами из его прайса).

### Задача

Необходимо разработать backend-часть сервиса заказа товаров для розничных сетей на Django Rest Framework.

**Базовая часть:**
* разработка сервиса под готовую спецификацию (API),
* возможность добавления настраиваемых полей (характеристик) товаров,
* импорт товаров,
* отправка накладной на email администратора (для исполнения заказа),
* отправка заказа на email клиента (подтверждение приёма заказа).

## Этапы разработки

1. Создание и настройка проекта.
2. Проработка моделей данных.
3. Реализация импорта товаров из файла shop.yaml.
4. Реализация API views.
5. Полностью готовый backend.

Разработку следует вести с использованием git (github/gitlab/bitbucket) с регулярными коммитами в репозиторий, доступный вашему дипломному руководителю. Старайтесь делать коммиты как можно чаще.

### Этап 1. Создание и настройка проекта

У вас создан базовый Django-проект, и он запускается без ошибок.

### Этап 2. Проработка моделей данных

Созданы модели и их дополнительные методы.

### Этап 3. Реализация импорта товаров

1. Созданы функции загрузки товаров из приложенных файлов в модели Django.
2. Загружены товары из всех файлов для импорта.

### Этап 4. Реализация APIViews

Реализованы API Views для основных страниц сервиса (без админки):
   - Авторизация
   - Регистрация
   - Получение списка товаров
   - Получение спецификации по отдельному товару в базе данных
   - Работа с корзиной (добавление, удаление товаров)
   - Добавление/удаление адреса доставки
   - Подтверждение заказа
   - Отправка email c подтверждением
   - Получение списка заказов
   - Получение деталей заказа
   - Редактирование статуса заказа

### Этап 5. Полностью готовый backend

1. Полностью работающие API Endpoint'ы
2. Корректно отрабатывает следующий сценарий:
   - пользователь может авторизироваться,
   - есть возможность отправки данных для регистрации и получения email с подтверждением регистрации,
   - пользователь может добавлять в корзину товары от разных магазинов,
   - пользователь может подтверждать заказ с вводом адреса доставки,
   - пользователь получает email с подтверждением после ввода адреса доставки,
   - пользователь может переходить на страницу «Заказы» и открывать созданный заказ.

---

## Правила приёма дипломной работы

1. Проект разместить в GitHub. Ссылка на дипломную работу должна оставаться неизменной, чтобы дипломный руководитель мог видеть ваш прогресс.
2. Сдавать финальный вариант дипломной работы в личном кабинете Нетологии.

-----

## Критерии оценки

Зачёт по дипломной работе можно получить, если работа соответствует критериям:

* работоспособный проект в репозитории с документацией по запуску,
* выполненная базовая часть проекта,
* наличие собственных комментариев к коду,
* использование сторонних библиотек и фреймворков.