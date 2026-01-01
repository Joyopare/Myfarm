from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile, FarmerProfile, FarmerRating

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'age', 'location', 'profile_picture')
        }),
    )

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'get_phone', 'dietary_preferences')
    search_fields = ('user__username', 'user__email', 'dietary_preferences')
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_phone(self, obj):
        return obj.user.phone
    get_phone.short_description = 'Phone'

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_location', 'is_verified', 'total_sales', 'average_rating', 'total_followers')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__email', 'farm_location')
    readonly_fields = ('total_sales', 'average_rating', 'total_followers')

@admin.register(FarmerRating)
class FarmerRatingAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('farmer__user__username', 'customer__user__username')
