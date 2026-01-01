from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from .forms import CustomerRegistrationForm, FarmerRegistrationForm, CustomLoginForm
from .models import User, CustomerProfile, FarmerProfile, FarmerRating

def home(request):
    return render(request, 'accounts/home.html')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('accounts:home')
    
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        response = super().form_valid(form)
        # Ensure session is saved
        if not self.request.session.session_key:
            self.request.session.create()
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return response

class CustomerRegistrationView(CreateView):
    form_class = CustomerRegistrationForm
    template_name = 'accounts/customer_register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Customer account created successfully! Please log in.')
        return response

class FarmerRegistrationView(CreateView):
    form_class = FarmerRegistrationForm
    template_name = 'accounts/farmer_register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Farmer account created successfully! Please log in.')
        return response

def register_choice(request):
    return render(request, 'accounts/register_choice.html')

@login_required
def profile(request):
    if request.user.user_type == 'customer':
        try:
            profile = request.user.customer_profile
        except CustomerProfile.DoesNotExist:
            CustomerProfile.objects.create(user=request.user)
            profile = request.user.customer_profile
        return render(request, 'accounts/customer_profile.html', {'profile': profile})
    else:
        try:
            profile = request.user.farmer_profile
        except FarmerProfile.DoesNotExist:
            FarmerProfile.objects.create(user=request.user, farm_location='')
            profile = request.user.farmer_profile
        return render(request, 'accounts/farmer_profile.html', {'profile': profile})

@login_required
def rate_farmer(request, farmer_id):
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can rate farmers.')
        return redirect('accounts:home')
    
    farmer = get_object_or_404(FarmerProfile, id=farmer_id)
    customer = request.user.customer_profile
    
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        review_text = request.POST.get('review', '')
        
        rating, created = FarmerRating.objects.update_or_create(
            farmer=farmer,
            customer=customer,
            defaults={
                'rating': rating_value,
                'review': review_text
            }
        )
        
        # No need to update average_rating as it's calculated dynamically
        
        action = 'updated' if not created else 'added'
        messages.success(request, f'Rating {action} successfully!')
        return redirect('products:farmer_products', farmer_id=farmer.id)
    
    # Check if customer has already rated this farmer
    existing_rating = FarmerRating.objects.filter(farmer=farmer, customer=customer).first()
    
    return render(request, 'accounts/rate_farmer.html', {
        'farmer': farmer,
        'existing_rating': existing_rating
    })

@login_required
def follow_farmer(request, farmer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can follow farmers'}, status=403)
    
    try:
        farmer = get_object_or_404(FarmerProfile, id=farmer_id)
        
        # Ensure customer profile exists
        try:
            customer = request.user.customer_profile
        except CustomerProfile.DoesNotExist:
            CustomerProfile.objects.create(user=request.user)
            customer = request.user.customer_profile
        
        if farmer.followers.filter(id=customer.id).exists():
            farmer.followers.remove(customer)
            following = False
            message = f'Unfollowed {farmer.user.username}'
        else:
            farmer.followers.add(customer)
            following = True
            message = f'Now following {farmer.user.username}'
            
            # Create notification for farmer
            try:
                from messaging.models import Notification
                Notification.objects.create(
                    user=farmer.user,
                    notification_type='new_follower',
                    title='New Follower',
                    message=f'{customer.user.username} is now following you!'
                )
            except Exception as e:
                # Log the error but don't fail the follow action
                print(f"Failed to create notification: {e}")
        
        return JsonResponse({
            'success': True,
            'following': following,
            'message': message,
            'followers_count': farmer.total_followers
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def edit_profile(request):
    if request.user.user_type == 'customer':
        try:
            profile = request.user.customer_profile
        except CustomerProfile.DoesNotExist:
            profile = CustomerProfile.objects.create(user=request.user)
        
        if request.method == 'POST':
            # Update user fields
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.phone = request.POST.get('phone', '')
            request.user.age = request.POST.get('age') or None
            request.user.location = request.POST.get('location', '')
            
            # Handle profile picture
            if 'profile_picture' in request.FILES:
                request.user.profile_picture = request.FILES['profile_picture']
            
            request.user.save()
            
            # Update customer profile fields
            profile.dietary_preferences = request.POST.get('dietary_preferences', '')
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        
        return render(request, 'accounts/edit_customer_profile.html', {
            'profile': profile
        })
    
    else:  # farmer
        try:
            profile = request.user.farmer_profile
        except FarmerProfile.DoesNotExist:
            profile = FarmerProfile.objects.create(user=request.user, farm_location='')
        
        if request.method == 'POST':
            # Update user fields
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.phone = request.POST.get('phone', '')
            request.user.age = request.POST.get('age') or None
            request.user.location = request.POST.get('location', '')
            
            # Handle profile picture
            if 'profile_picture' in request.FILES:
                request.user.profile_picture = request.FILES['profile_picture']
            
            request.user.save()
            
            # Update farmer profile fields
            profile.farm_name = request.POST.get('farm_name', '')
            profile.farm_location = request.POST.get('farm_location', '')
            profile.farm_description = request.POST.get('farm_description', '')
            profile.years_of_experience = request.POST.get('years_of_experience') or 0
            profile.farming_methods = request.POST.get('farming_methods', '')
            
            # Handle verification documents
            if 'verification_documents' in request.FILES:
                profile.verification_documents = request.FILES['verification_documents']
            
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        
        return render(request, 'accounts/edit_farmer_profile.html', {
            'profile': profile
        })
