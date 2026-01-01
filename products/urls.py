from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('farmer/<int:farmer_id>/', views.FarmerProductsView.as_view(), name='farmer_products'),
    path('category/<int:category_id>/', views.CategoryProductsView.as_view(), name='category_products'),
    
    # Farmer URLs
    path('dashboard/', views.FarmerDashboardView.as_view(), name='farmer_dashboard'),
    path('add/', views.ProductCreateView.as_view(), name='product_add'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('<int:pk>/toggle-availability/', views.toggle_product_availability, name='toggle_availability'),
    
    # AJAX endpoints
    path('search/', views.product_search_api, name='product_search_api'),
    path('advanced-search/', views.AdvancedSearchView.as_view(), name='advanced_search'),
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('review/<int:product_id>/', views.add_product_review, name='add_product_review'),
]
