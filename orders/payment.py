import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Order

# Set Stripe API key
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')

class StripePaymentProcessor:
    def __init__(self):
        self.stripe = stripe
    
    def create_payment_intent(self, order):
        """Create a Stripe Payment Intent for the order"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'customer_email': order.customer.user.email
                }
            )
            return intent
        except stripe.error.StripeError as e:
            return None
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment and update order status"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == 'succeeded':
                order_id = intent.metadata.get('order_id')
                if order_id:
                    order = Order.objects.get(id=order_id)
                    order.status = 'confirmed'
                    order.save()
                    return True
            return False
        except (stripe.error.StripeError, Order.DoesNotExist):
            return False

def process_payment(request):
    """Process payment for an order"""
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        order = get_object_or_404(Order, order_number=order_number, customer=request.user.customer_profile)
        
        processor = StripePaymentProcessor()
        intent = processor.create_payment_intent(order)
        
        if intent:
            return JsonResponse({
                'success': True,
                'client_secret': intent.client_secret,
                'publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
            })
        else:
            return JsonResponse({'success': False, 'error': 'Payment processing failed'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
