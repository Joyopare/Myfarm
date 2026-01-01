from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('farmer', 'Farmer'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    dietary_preferences = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Customer: {self.user.username}"

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200, blank=True)
    farm_location = models.CharField(max_length=200)
    farm_description = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    farming_methods = models.CharField(max_length=200, blank=True)
    followers = models.ManyToManyField(CustomerProfile, blank=True, related_name='following')
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_documents = models.FileField(upload_to='verification/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - Farmer"
    
    @property
    def total_followers(self):
        return self.followers.count()
    
    @property
    def total_sales(self):
        from orders.models import OrderItem
        result = OrderItem.objects.filter(product__farmer=self).aggregate(
            total=models.Sum('quantity')
        )['total']
        return result or 0
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0

class FarmerRating(models.Model):
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('farmer', 'customer')
    
    def __str__(self):
        return f"{self.customer.user.username} rated {self.farmer.user.username}: {self.rating} stars"
