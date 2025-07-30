from django.urls import path
from .views import (
    ItemDetailView,
    CreateOrderView,
    CreatePaymentIntentView,
    CheckoutView,
    SuccessView,
)

app_name = 'store'

urlpatterns = [
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('order/create/', CreateOrderView.as_view(), name='create_order'),
    path('buy/<int:pk>/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('checkout/<int:pk>/', CheckoutView.as_view(), name='checkout'),
    path('success/', SuccessView.as_view(), name='success'),
]