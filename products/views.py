from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from .models import Product, Category, ProductReview
from .forms import ProductForm
from accounts.models import FarmerProfile
from orders.models import Order, OrderItem
from messaging.models import Notification

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('farmer__user', 'category')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(farmer__user__username__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Location filter
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(farmer__farm_location__icontains=location)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['location'] = self.request.GET.get('location', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        return context

class FarmerProductsView(ListView):
    model = Product
    template_name = 'products/farmer_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.farmer = get_object_or_404(FarmerProfile, id=self.kwargs['farmer_id'])
        return Product.objects.filter(farmer=self.farmer, is_available=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['farmer'] = self.farmer
        return context

class CategoryProductsView(ListView):
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        return Product.objects.filter(category=self.category, is_available=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class FarmerDashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/farmer_dashboard.html'
    context_object_name = 'products'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            messages.error(request, 'Access denied. Farmers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Product.objects.filter(farmer=self.request.user.farmer_profile).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        farmer = self.request.user.farmer_profile
        
        # Dashboard statistics
        context['total_products'] = farmer.products.count()
        context['active_products'] = farmer.products.filter(is_available=True).count()
        context['total_sales'] = farmer.total_sales
        context['total_followers'] = farmer.total_followers
        context['average_rating'] = farmer.average_rating
        
        # Recent orders
        context['recent_orders'] = OrderItem.objects.filter(
            farmer=farmer
        ).select_related('order', 'product').order_by('-order__created_at')[:5]
        
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:farmer_dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            messages.error(request, 'Access denied. Farmers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.farmer = self.request.user.farmer_profile
        messages.success(self.request, 'Product added successfully!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:farmer_dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if request.user.user_type != 'farmer' or product.farmer != request.user.farmer_profile:
            messages.error(request, 'Access denied.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:farmer_dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if request.user.user_type != 'farmer' or product.farmer != request.user.farmer_profile:
            messages.error(request, 'Access denied.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def toggle_product_availability(request, pk):
    if request.user.user_type != 'farmer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    product = get_object_or_404(Product, pk=pk, farmer=request.user.farmer_profile)
    product.is_available = not product.is_available
    product.save()
    
    return JsonResponse({
        'success': True,
        'is_available': product.is_available,
        'status': 'Available' if product.is_available else 'Unavailable'
    })

def product_search_api(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True
        )[:10]
        
        results = [{
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'farmer': product.farmer.user.username,
            'image_url': product.image.url if product.image else ''
        } for product in products]
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})

@login_required
def add_product_review(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can review products'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review', '')
        
        if not (1 <= rating <= 5):
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        review, created = ProductReview.objects.update_or_create(
            product=product,
            customer=request.user.customer_profile,
            defaults={
                'rating': rating,
                'review': review_text
            }
        )
        
        # Create notification for farmer
        Notification.objects.create(
            user=product.farmer.user,
            type='review',
            title='New Product Review',
            message=f'{request.user.username} reviewed your product "{product.name}" with {rating} stars.'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!',
            'rating': rating,
            'created': created
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

class AdvancedSearchView(ListView):
    model = Product
    template_name = 'products/advanced_search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('farmer__user', 'category')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(farmer__user__username__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Location filter
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(farmer__farm_location__icontains=location)
        
        # Rating filter
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            # This would require a more complex query with annotations
            pass
        
        # Stock filter
        in_stock = self.request.GET.get('in_stock')
        if in_stock:
            queryset = queryset.filter(stock__gt=0)
        
        # Organic filter
        organic = self.request.GET.get('organic')
        if organic:
            queryset = queryset.filter(
                Q(name__icontains='organic') |
                Q(description__icontains='organic') |
                Q(farmer__farming_methods__icontains='organic')
            )
        
        # Sorting
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            # Would need annotation for average rating
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            # Would need annotation for popularity
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['location'] = self.request.GET.get('location', '')
        context['min_rating'] = self.request.GET.get('min_rating', '')
        context['in_stock'] = self.request.GET.get('in_stock')
        context['organic'] = self.request.GET.get('organic')
        context['sort'] = self.request.GET.get('sort', 'newest')
        return context

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'products/analytics_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            messages.error(request, 'Access denied. Farmers only.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        farmer = self.request.user.farmer_profile
        
        # Basic metrics
        from django.db.models import Sum, Count, Avg
        from datetime import datetime, timedelta
        
        orders = OrderItem.objects.filter(farmer=farmer)
        context['total_revenue'] = orders.aggregate(Sum('price'))['price__sum'] or 0
        context['total_orders'] = orders.count()
        context['total_customers'] = orders.values('order__customer').distinct().count()
        context['avg_rating'] = farmer.average_rating
        
        # Top products
        context['top_products'] = Product.objects.filter(farmer=farmer).annotate(
            total_sold=Count('orderitem'),
            total_revenue=Sum('orderitem__price')
        ).order_by('-total_sold')[:5]
        
        # Sample data for charts (in production, calculate from real data)
        context['sales_dates'] = ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']
        context['sales_amounts'] = [100, 150, 200, 175, 225]
        context['category_names'] = ['Vegetables', 'Fruits', 'Grains', 'Dairy']
        context['category_sales'] = [30, 25, 20, 25]
        context['customer_demographics'] = [15, 25, 30, 20, 10]
        context['order_patterns'] = [10, 15, 20, 18, 22, 25, 12]
        
        # Recent activities (sample data)
        context['recent_activities'] = [
            {'title': 'New Order', 'description': 'Order #1234 received', 'created_at': datetime.now()},
            {'title': 'Product Added', 'description': 'Fresh Tomatoes added', 'created_at': datetime.now() - timedelta(hours=2)},
            {'title': 'Review Received', 'description': '5-star review on Carrots', 'created_at': datetime.now() - timedelta(hours=5)},
        ]
        
        return context
