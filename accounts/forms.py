from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, CustomerProfile, FarmerProfile

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=17, required=True)
    location = forms.CharField(max_length=255, required=True)
    age = forms.IntegerField(required=True, min_value=13, max_value=120)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'location', 'age', 'profile_picture', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.location = self.cleaned_data['location']
        user.age = self.cleaned_data['age']
        user.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            user.save()
            CustomerProfile.objects.create(user=user)
        return user

class FarmerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=17, required=True)
    location = forms.CharField(max_length=255, required=True)
    farm_location = forms.CharField(max_length=255, required=True)
    age = forms.IntegerField(required=True, min_value=18, max_value=120)
    profile_picture = forms.ImageField(required=False)
    proof_of_farming = forms.FileField(required=False, help_text="Optional: Upload proof of farming for verification")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'location', 'age', 'profile_picture', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'farmer'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.location = self.cleaned_data['location']
        user.age = self.cleaned_data['age']
        user.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            user.save()
            FarmerProfile.objects.create(
                user=user,
                farm_location=self.cleaned_data['farm_location'],
                verification_documents=self.cleaned_data['proof_of_farming']
            )
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username, Email or Phone'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        # Allow login with email or phone
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        elif username.isdigit() or username.startswith('+'):
            try:
                user = User.objects.get(phone=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username
