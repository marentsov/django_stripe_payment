import pytest
import json
from django.urls import reverse
from django.test import RequestFactory, Client
from unittest.mock import Mock
from .models import Item, Order, OrderItem
from .views import CreatePaymentIntentView
from django.contrib.auth.models import User

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def item_usd():
    return Item.objects.create(name='Test Item USD', price=10.00, currency='USD')

@pytest.fixture
def item_eur():
    return Item.objects.create(name='Test Item EUR', price=10.00, currency='EUR')

@pytest.fixture
def order(item_usd):
    order = Order.objects.create()
    OrderItem.objects.create(order=order, item=item_usd, quantity=1)
    return order

@pytest.mark.django_db
def test_item_list_view(client):
    response = client.get(reverse('store:item_list'))
    assert response.status_code == 200
    assert 'items' in response.context

@pytest.mark.django_db
def test_item_detail_view(item_usd, client):
    response = client.get(reverse('store:item_detail', kwargs={'pk': item_usd.pk}))
    assert response.status_code == 200
    assert response.context['item'] == item_usd
    assert 'stripe_publishable_key' in response.context

@pytest.mark.django_db
def test_create_order_view_valid(client, item_usd):
    response = client.post(reverse('store:create_order'), {
        'item_ids': [item_usd.pk],
        'quantities': [1]
    })
    assert response.status_code == 302
    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1

@pytest.mark.django_db
def test_create_order_view_invalid_quantity(client, item_usd):
    response = client.post(reverse('store:create_order'), {
        'item_ids': [item_usd.pk],
        'quantities': [0]
    })
    assert response.status_code == 302
    assert Order.objects.count() == 0

@pytest.mark.django_db
def test_create_payment_intent_view_success(order, request_factory, mocker):
    request = request_factory.get(reverse('store:create_payment_intent', kwargs={'pk': order.pk}))
    payment_intent_mock = Mock(id='pi_123', client_secret='secret_123')
    mocker.patch('stripe.PaymentIntent.create', return_value=payment_intent_mock)
    response = CreatePaymentIntentView.as_view()(request, pk=order.pk)
    assert response.status_code == 200
    assert 'client_secret' in response.json()


@pytest.mark.django_db
def test_create_payment_intent_view_success(order, request_factory, mocker):
    request = request_factory.get(reverse('store:create_payment_intent', kwargs={'pk': order.pk}))
    payment_intent_mock = Mock(id='pi_123', client_secret='secret_123')
    mocker.patch('stripe.PaymentIntent.create', return_value=payment_intent_mock)
    response = CreatePaymentIntentView.as_view()(request, pk=order.pk)
    assert response.status_code == 200
    assert 'client_secret' in json.loads(response.content.decode())

@pytest.mark.django_db
def test_checkout_view_success(order, client):
    response = client.get(reverse('store:checkout', kwargs={'pk': order.pk}))
    assert response.status_code == 200
    assert 'order' in response.context
    assert 'stripe_publishable_key' in response.context

@pytest.mark.django_db
def test_create_payment_intent_view_order_not_found(request_factory):
    request = request_factory.get(reverse('store:create_payment_intent', kwargs={'pk': 999}))
    response = CreatePaymentIntentView.as_view()(request, pk=999)
    assert response.status_code == 404
    assert json.loads(response.content.decode())['error'] == 'Заказ не найден'

@pytest.mark.django_db
def test_success_view(client):
    response = client.get(reverse('store:success'))
    assert response.status_code == 200
    assert 'message' in response.context