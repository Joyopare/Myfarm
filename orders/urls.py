from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<str:order_number>/', views.PaymentMethodView.as_view(), name='payment_method'),
    path('payment-confirmation/<str:order_number>/', views.PaymentConfirmationView.as_view(), name='payment_confirmation'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('process-mobile-payment/', views.process_mobile_payment, name='process_mobile_payment'),
    path('process-cod-payment/', views.process_cod_payment, name='process_cod_payment'),
    path('order-confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('order-history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('order-detail/<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('process-payment/', views.process_payment, name='process_payment'),
]
