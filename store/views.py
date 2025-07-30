import stripe
from django.conf import settings
from django.views.generic import DetailView, View
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import Item, Order, OrderItem

class ItemDetailView(DetailView):
    model = Item
    template_name = 'item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY_USD \
            if self.object.currency == 'USD' \
            else settings.STRIPE_PUBLISHABLE_KEY_EUR
        return context

class CreateOrderView(View):
    def post(self, request):
        item_ids = request.POST.getlist('item_ids')
        quantities = request.POST.getlist('quantities')
        discount_id = request.POST.get('discount_id')
        tax_id = request.POST.get('tax_id')

        order = Order.objects.create(
            discount_id=discount_id or None,
            tax_id=tax_id or None
        )
        for item_id, quantity in zip(item_ids, quantities):
            OrderItem.objects.create(
                order=order,
                item_id=item_id,
                quantity=int(quantity)
            )
        return redirect('store:checkout', pk=order.id)

class CreatePaymentIntentView(View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        items = order.items.all()
        if not items:
            return JsonResponse({'error': 'Заказ пуст'}, status=400)

        # Проверка, что все товары имеют одну валюту
        currency = items[0].currency
        if not all(item.currency == currency for item in items):
            return JsonResponse({'error': 'Все товары должны иметь одну валюту'}, status=400)

        # Установка ключа Stripe в зависимости от валюты
        stripe.api_key = settings.STRIPE_SECRET_KEY_USD if currency == 'USD' else settings.STRIPE_SECRET_KEY_EUR

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.get_total() * 100),  # Конвертация в центы
                currency=currency.lower(),
                payment_method_types=['card'],
                metadata={'order_id': order.id},
            )
            order.payment_intent_id = payment_intent.id
            order.save()
            return JsonResponse({'client_secret': payment_intent.client_secret})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)


class CheckoutView(View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        items = order.items.all()
        if not items:
            return redirect('store:item_detail', pk=items[0].id if items else 1)  # Перенаправление, если заказ пуст
        currency = items[0].currency
        stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY_USD if currency == 'USD' else settings.STRIPE_PUBLISHABLE_KEY_EUR
        return render(request, 'checkout.html', {
            'order': order,
            'stripe_publishable_key': stripe_publishable_key
        })


class SuccessView(View):
    def get(self, request):
        return render(request, 'success.html', {'message': 'Оплата успешно завершена!'})
# Create your views here.
