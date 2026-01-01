from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'get_total_items', 'get_total_price', 'created_at')
    search_fields = ('customer__user__username',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return obj.total_items
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return f"${obj.total_price:.2f}"
    get_total_price.short_description = 'Total Price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total_price')
    search_fields = ('cart__customer__user__username', 'product__name')
    
    def get_total_price(self, obj):
        return f"${obj.total_price:.2f}"
    get_total_price.short_description = 'Total Price'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'delivery_option', 'total_amount', 'created_at')
    list_filter = ('status', 'delivery_option', 'created_at')
    search_fields = ('order_number', 'customer__user__username')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Delivery', {
            'fields': ('delivery_option', 'delivery_address')
        }),
        ('Payment', {
            'fields': ('total_amount',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'farmer', 'quantity', 'price', 'get_total_price')
    search_fields = ('order__order_number', 'product__name', 'farmer__user__username')
    list_filter = ('order__status',)
    
    def get_total_price(self, obj):
        return f"${obj.total_price:.2f}"
    get_total_price.short_description = 'Total Price'
