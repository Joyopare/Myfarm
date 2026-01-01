from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
from .payment import process_payment
from products.models import Product
from messaging.models import Notification
import uuid
from django.utils import timezone
from django.conf import settings
import json

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cart.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.user_type != 'customer':
            messages.error(request, 'Access denied. Customers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(customer=self.request.user.customer_profile)
        context['cart'] = cart
        return context

@login_required
def add_to_cart(request, product_id):
    if not request.user.is_authenticated or request.user.user_type != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    customer = request.user.customer_profile
    cart, created = Cart.objects.get_or_create(customer=customer)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        return JsonResponse({'error': 'Not enough stock available'}, status=400)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            return JsonResponse({'error': 'Not enough stock available'}, status=400)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart',
        'cart_total': cart.total_items
    })

@login_required
def update_cart_item(request, item_id):
    if not request.user.is_authenticated or request.user.user_type != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer_profile)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > cart_item.product.stock:
        return JsonResponse({'error': 'Not enough stock available'}, status=400)
    
    if quantity <= 0:
        cart_item.delete()
        return JsonResponse({'success': True, 'removed': True})
    
    cart_item.quantity = quantity
    cart_item.save()
    
    return JsonResponse({
        'success': True,
        'item_total': cart_item.total_price,
        'cart_total': cart_item.cart.total_price
    })

@login_required
def remove_from_cart(request, item_id):
    if not request.user.is_authenticated or request.user.user_type != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer_profile)
    cart_item.delete()
    
    return JsonResponse({'success': True, 'message': 'Item removed from cart'})

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/checkout.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.user_type != 'customer':
            messages.error(request, 'Access denied. Customers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_object_or_404(Cart, customer=self.request.user.customer_profile)
        if not cart.items.exists():
            messages.error(self.request, 'Your cart is empty.')
            return redirect('orders:cart')
        
        context['cart'] = cart
        context['form'] = CheckoutForm()
        return context
    
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, customer=request.user.customer_profile)
        form = CheckoutForm(request.POST)
        
        if form.is_valid() and cart.items.exists():
            # Create order
            order = Order.objects.create(
                customer=request.user.customer_profile,
                order_number=self.generate_order_number(),
                delivery_option=form.cleaned_data['delivery_option'],
                delivery_address=form.cleaned_data['delivery_address'],
                total_amount=cart.total_price
            )
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    farmer=cart_item.product.farmer,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Redirect to payment method selection instead of clearing cart immediately
            messages.success(request, 'Order created successfully! Please complete payment.')
            return redirect('orders:payment_method', order_number=order.order_number)
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)
    
    def generate_order_number(self):
        return f"ORD-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

class PaymentMethodView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/payment_method.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.user_type != 'customer':
            messages.error(request, 'Access denied. Customers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = kwargs.get('order_number')
        order = get_object_or_404(Order, order_number=order_number, customer=self.request.user.customer_profile)
        context['order'] = order
        context['stripe_publishable_key'] = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        return context

class PaymentConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/payment_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = kwargs.get('order_number')
        order = get_object_or_404(Order, order_number=order_number, customer=self.request.user.customer_profile)
        context['order'] = order
        return context

@login_required
def create_payment_intent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        payment_method = data.get('payment_method')
        
        order = get_object_or_404(Order, order_number=order_number, customer=request.user.customer_profile)
        
        if payment_method == 'credit_card':
            from .payment import StripePaymentProcessor
            processor = StripePaymentProcessor()
            intent = processor.create_payment_intent(order)
            
            if intent:
                order.payment_intent_id = intent.id
                order.payment_method = 'Credit Card'
                order.payment_status = 'processing'
                order.save()
                
                return JsonResponse({
                    'success': True,
                    'client_secret': intent.client_secret
                })
        
        return JsonResponse({'success': False, 'error': 'Invalid payment method'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def confirm_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        order_number = data.get('order_number')
        
        order = get_object_or_404(Order, order_number=order_number, customer=request.user.customer_profile)
        
        from .payment import StripePaymentProcessor
        processor = StripePaymentProcessor()
        
        if processor.confirm_payment(payment_intent_id):
            order.payment_status = 'completed'
            order.status = 'confirmed'
            order.save()
            
            # Update product stock and clear cart
            for order_item in order.items.all():
                order_item.product.stock -= order_item.quantity
                order_item.product.save()
            
            # Clear customer's cart
            cart = Cart.objects.filter(customer=request.user.customer_profile).first()
            if cart:
                cart.items.all().delete()
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Payment confirmation failed'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def process_mobile_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        provider = data.get('provider')
        phone_number = data.get('phone_number')
        
        order = get_object_or_404(Order, order_number=order_number, customer=request.user.customer_profile)
        
        # Simulate mobile money processing
        order.payment_method = f'Mobile Money ({provider.upper()})'
        order.payment_status = 'completed'
        order.status = 'confirmed'
        order.save()
        
        # Update product stock and clear cart
        for order_item in order.items.all():
            order_item.product.stock -= order_item.quantity
            order_item.product.save()
        
        # Clear customer's cart
        cart = Cart.objects.filter(customer=request.user.customer_profile).first()
        if cart:
            cart.items.all().delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def process_cod_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        
        order = get_object_or_404(Order, order_number=order_number, customer=request.user.customer_profile)
        
        order.payment_method = 'Cash on Delivery'
        order.payment_status = 'pending'
        order.status = 'confirmed'
        order.save()
        
        # Update product stock and clear cart
        for order_item in order.items.all():
            order_item.product.stock -= order_item.quantity
            order_item.product.save()
        
        # Clear customer's cart
        cart = Cart.objects.filter(customer=request.user.customer_profile).first()
        if cart:
            cart.items.all().delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

class OrderConfirmationView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer_profile)

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.user_type != 'customer':
            messages.error(request, 'Access denied. Customers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer_profile).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['show_payment_info'] = order.payment_status in ['completed', 'processing']
        return context
