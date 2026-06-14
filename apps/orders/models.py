from django.db import models
from django.conf import settings
from apps.catalog.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )
    DELIVERY_EXPRESS = 'express'
    DELIVERY_STANDARD = 'standard'
    DELIVERY_PICKUP = 'pickup'
    DELIVERY_CHOICES = (
        (DELIVERY_EXPRESS, 'Экспресс (от 2 часов)'),
        (DELIVERY_STANDARD, 'Стандарт (выбранный интервал)'),
        (DELIVERY_PICKUP, 'Самовывоз из салона'),
    )
    PAYMENT_CARD_ONLINE = 'card_online'
    PAYMENT_CARD_COURIER = 'card_courier'
    PAYMENT_CASH = 'cash'
    PAYMENT_CHOICES = (
        (PAYMENT_CARD_ONLINE, 'Картой онлайн'),
        (PAYMENT_CARD_COURIER, 'Картой курьеру'),
        (PAYMENT_CASH, 'Наличными при получении'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.CharField(max_length=250, verbose_name='Адрес')
    postal_code = models.CharField(max_length=20, verbose_name='Индекс', blank=True)
    city = models.CharField(max_length=100, verbose_name='Город')
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default=DELIVERY_STANDARD,
        verbose_name='Способ доставки',
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_CARD_ONLINE,
        verbose_name='Способ оплаты',
    )
    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость доставки',
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    paid = models.BooleanField(default=False, verbose_name='Оплачен')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ {self.id} от {self.first_name}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_grand_total(self):
        return self.get_total_cost() + self.delivery_cost

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity
