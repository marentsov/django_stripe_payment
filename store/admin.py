from django.contrib import admin
from .models import Item, Order, OrderItem, Discount, Tax

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency', 'description']
    list_filter = ['currency']
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'get_total']
    list_filter = ['created_at']
    search_fields = ['id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'quantity']
    list_filter = ['order']
    search_fields = ['item__name', 'item__description', 'order__id']

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent']
    search_fields = ['name']

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate']
    search_fields = ['name']
# Register your models here.
