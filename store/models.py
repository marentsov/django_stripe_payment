from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
    currency = models.CharField(
        max_length=3,
        choices=[('USD', 'USD'), ('EUR', 'EUR')],
        default='USD',
        verbose_name='Валюта оплаты'
    )
    discount = models.ForeignKey(
        to='Discount',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Скидка'
    )
    tax = models.ForeignKey(
        to='Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Налог'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.name}, {self.price} ({self.currency})'


class Discount(models.Model):
    name = models.CharField(max_length=155, verbose_name='Название')
    percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Процент')

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        return f'{self.name} - {self.percent} %'

class Tax(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ставка')

    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'

    def __str__(self):
        return f'{self.name} - {self.rate} %'


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    items = models.ManyToManyField(Item, through='OrderItem', verbose_name='Товары')
    discount = models.ForeignKey(to=Discount, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Скидка')
    tax = models.ForeignKey(Tax, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Налог')
    payment_intent_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='ID платежа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_total(self):
        order_items = self.orderitem_set.all()
        if not order_items:
            return 0.00
        currencies = {order_item.item.currency for order_item in order_items}
        if len(currencies) > 1:
            raise ValueError("Все товары в заказе должны иметь одну валюту")
        total = 0
        for order_item in order_items:
            item_total = order_item.item.price * order_item.quantity
            if order_item.item.discount:
                item_total *= (1 - (order_item.item.discount.percent / 100))
            if order_item.item.tax:
                item_total *= (1 + (order_item.item.tax.rate / 100))
            total += item_total
        if self.discount:
            total *= (1 - (self.discount.percent / 100))
        if self.tax:
            total *= (1 + (self.tax.rate / 100))
        return round(total, 2)

    def __str__(self):
        return f'Заказ {self.id} от {self.created_at}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Состав заказа'
        verbose_name_plural = 'Состав заказов'

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


# Create your models here.
