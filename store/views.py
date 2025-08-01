import stripe
from django.conf import settings
from django.views.generic import DetailView, ListView, View
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib import messages
from .models import Item, Order, OrderItem, Discount, Tax
import logging

log = logging.getLogger('stripe_app')

class ItemListView(ListView):
    model = Item
    template_name = 'item_list.html'
    context_object_name = 'items'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY_USD if self.object.currency == 'USD' else settings.STRIPE_PUBLISHABLE_KEY_EUR
        return context

class CreateOrderView(View):
    def post(self, request):
        try:
            item_ids = request.POST.getlist('item_ids')
            quantities = request.POST.getlist('quantities')
            log.info(f"Creating order with items: {item_ids}, quantities: {quantities}")

            if not item_ids or not quantities or len(item_ids) != len(quantities):
                log.error("Invalid items or quantities provided")
                messages.error(request, 'Неверные товары или количество.')
                return redirect('store:item_list')

            items = Item.objects.filter(id__in=item_ids)
            if len(items) != len(item_ids):
                log.error("Some items not found")
                messages.error(request, 'Некоторые товары не найдены.')
                return redirect('store:item_list')

            # Проверяем, что все товары имеют одну валюту
            currencies = {item.currency for item in items}
            if len(currencies) > 1:
                log.warning("Items have different currencies")
                messages.error(request, 'Все товары в заказе должны иметь одну валюту.')
                return redirect('store:item_list')

            order = Order.objects.create()
            for item_id, quantity in zip(item_ids, quantities):
                try:
                    item = items.get(id=item_id)
                    qty = int(quantity)
                    if qty < 1:
                        log.error(f"Invalid quantity for item {item_id}: {quantity}")
                        messages.error(request, 'Количество должно быть положительным.')
                        return redirect('store:item_list')
                    OrderItem.objects.create(
                        order=order,
                        item=item,
                        quantity=qty
                    )
                except ValueError:
                    log.error(f"Invalid quantity for item {item_id}: {quantity}")
                    messages.error(request, f'Неверное количество для товара {item_id}.')
                    return redirect('store:item_list')

            log.info(f"Order {order.id} created successfully with {len(item_ids)} items")
            return redirect('store:checkout', pk=order.id)

        except Exception as e:
            log.critical(f"Failed to create order: error - {str(e)}")
            messages.error(request, 'Произошла ошибка при создании заказа.')
            return redirect('store:item_list')

class CreatePaymentIntentView(View):
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            items = order.items.all()
            log.info(f"Creating PaymentIntent for order {order.id}")

            if not items:
                log.warning(f"Order {order.id} is empty")
                return JsonResponse({'error': 'Заказ пуст'}, status=400)

            # Проверяем валюты (хотя это уже проверено в CreateOrderView)
            currencies = {item.currency for item in items}
            if len(currencies) > 1:
                log.error(f"Order {order.id} contains items with mixed currencies")
                return JsonResponse({'error': 'Все товары должны иметь одну валюту'}, status=400)

            currency = items[0].currency
            stripe.api_key = settings.STRIPE_SECRET_KEY_USD if currency == 'USD' else settings.STRIPE_SECRET_KEY_EUR

            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.get_total() * 100),
                currency=currency.lower(),
                payment_method_types=['card'],
                metadata={
                    'order_id': order.id,
                    'discount': f"{order.discount.name} ({order.discount.percent}%)" if order.discount else 'None',
                    'tax': f"{order.tax.name} ({order.tax.rate}%)" if order.tax else 'None'
                },
            )
            order.payment_intent_id = payment_intent.id
            order.save()
            log.info(f"PaymentIntent {payment_intent.id} created for order {order.id}")
            return JsonResponse({'client_secret': payment_intent.client_secret})

        except Order.DoesNotExist:
            log.error(f"Order {pk} not found")
            return JsonResponse({'error': 'Заказ не найден'}, status=404)
        except stripe.error.StripeError as e:
            log.error(f"Stripe error for order {pk}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            log.critical(f"Unexpected error in PaymentIntent creation for order {pk}: {str(e)}")
            return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)

class CheckoutView(View):
    def get(self, request, pk):

        try:
            order = Order.objects.get(pk=pk)
            items = order.items.all()
            log.info(f"Accessing checkout for order {order.id}")

            if not items:
                log.warning(f"Redirecting from checkout for empty order {order.id}")
                messages.error(request, 'Заказ пуст.')
                return redirect('store:item_list')

            currency = items[0].currency
            stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY_USD if currency == 'USD' else settings.STRIPE_PUBLISHABLE_KEY_EUR
            return render(request, 'checkout.html', {
                'order': order,
                'stripe_publishable_key': stripe_publishable_key
            })

        except Order.DoesNotExist:
            log.error(f"Order {pk} not found")
            return render(request, '404.html', status=404)
        except Exception as e:
            log.critical(f"Unexpected error in checkout for order {pk}: {str(e)}")
            return render(request, '500.html', status=500)

class SuccessView(View):
    def get(self, request):
        log.info("Payment completed successfully")
        return render(request, 'success.html', {'message': 'Оплата успешно завершена!'})

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)