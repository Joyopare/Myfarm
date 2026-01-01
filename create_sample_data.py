#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmmarket.settings')
django.setup()

from accounts.models import User, CustomerProfile, FarmerProfile
from products.models import Category, Product

def create_sample_data():
    print("Creating sample data...")
    
    # Create categories
    categories = [
        {'name': 'Vegetables', 'description': 'Fresh vegetables'},
        {'name': 'Fruits', 'description': 'Fresh fruits'},
        {'name': 'Dairy', 'description': 'Dairy products'},
        {'name': 'Herbs', 'description': 'Fresh herbs and spices'},
        {'name': 'Grains', 'description': 'Grains and cereals'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create sample farmer
    farmer_user, created = User.objects.get_or_create(
        username='farmer_john',
        defaults={
            'email': 'john@farm.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'user_type': 'farmer',
            'phone': '+1234567890',
            'location': 'California',
            'age': 45
        }
    )
    
    if created:
        farmer_user.set_password('password123')
        farmer_user.save()
        print(f"Created farmer user: {farmer_user.username}")
    
    farmer_profile, created = FarmerProfile.objects.get_or_create(
        user=farmer_user,
        defaults={
            'farm_location': 'Sunny Valley Farm, California',
            'is_verified': True
        }
    )
    
    if created:
        print(f"Created farmer profile: {farmer_profile}")
    
    # Create sample customer
    customer_user, created = User.objects.get_or_create(
        username='customer_jane',
        defaults={
            'email': 'jane@customer.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'user_type': 'customer',
            'phone': '+1987654321',
            'location': 'Los Angeles',
            'age': 30
        }
    )
    
    if created:
        customer_user.set_password('password123')
        customer_user.save()
        print(f"Created customer user: {customer_user.username}")
    
    customer_profile, created = CustomerProfile.objects.get_or_create(
        user=customer_user
    )
    
    if created:
        print(f"Created customer profile: {customer_profile}")
    
    # Create sample products
    vegetables = Category.objects.get(name='Vegetables')
    fruits = Category.objects.get(name='Fruits')
    
    sample_products = [
        {
            'name': 'Organic Tomatoes',
            'description': 'Fresh organic tomatoes grown without pesticides',
            'category': vegetables,
            'price': 4.99,
            'stock': 50
        },
        {
            'name': 'Fresh Carrots',
            'description': 'Crisp and sweet carrots, perfect for cooking',
            'category': vegetables,
            'price': 2.99,
            'stock': 75
        },
        {
            'name': 'Sweet Apples',
            'description': 'Juicy red apples, great for snacking',
            'category': fruits,
            'price': 3.49,
            'stock': 100
        },
        {
            'name': 'Fresh Lettuce',
            'description': 'Crisp lettuce leaves for salads',
            'category': vegetables,
            'price': 1.99,
            'stock': 30
        },
        {
            'name': 'Organic Strawberries',
            'description': 'Sweet and juicy organic strawberries',
            'category': fruits,
            'price': 5.99,
            'stock': 25
        }
    ]
    
    for product_data in sample_products:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            farmer=farmer_profile,
            defaults={
                'description': product_data['description'],
                'category': product_data['category'],
                'price': product_data['price'],
                'stock': product_data['stock'],
                'is_available': True
            }
        )
        if created:
            print(f"Created product: {product.name}")
    
    print("Sample data creation completed!")

if __name__ == '__main__':
    create_sample_data()
