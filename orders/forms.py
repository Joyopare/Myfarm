from django import forms
from .models import Order

class CheckoutForm(forms.Form):
    DELIVERY_CHOICES = (
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    )
    
    delivery_option = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Enter pickup location or delivery address"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_address'].required = True
