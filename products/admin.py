from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'price', 'stock', 'is_available', 'average_rating', 'created_at')
    list_filter = ('category', 'is_available', 'created_at', 'farmer')
    search_fields = ('name', 'description', 'farmer__user__username')
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'total_reviews')
    list_editable = ('is_available', 'stock')
    
    fieldsets = (
        (None, {
            'fields': ('farmer', 'category', 'name', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_available')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Reviews', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'product__category')
    search_fields = ('product__name', 'customer__user__username', 'review')
    readonly_fields = ('created_at',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text')
    list_filter = ('product__category',)
    search_fields = ('product__name', 'alt_text')
