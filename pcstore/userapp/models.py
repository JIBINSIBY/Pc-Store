from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

def validate_rating(value):
    if value < 1 or value > 5:
        raise ValidationError('Rating must be between 1 and 5.')

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    
    fullname = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    mobile = models.CharField(max_length=20,unique=False,default="nil")
    # Use email as the unique identifier instead of username
    email = models.EmailField(unique=True)

    # If you want to use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','password']

    def _str_(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flat_house = models.CharField(max_length=255, default='Unknown')
    area_street = models.CharField(max_length=255, default='Unknown')
    landmark = models.CharField(max_length=255, blank=True, null=True, default='')
    pincode = models.CharField(max_length=20, default='000000')
    town_city = models.CharField(max_length=100, default='Unknown')
    state = models.CharField(max_length=100, default='Unknown')
    fullname = models.CharField(max_length=255, default='Unknown')
    mobile = models.CharField(max_length=20, default='Unknown')

    def __str__(self):
        return f"{self.flat_house}, {self.area_street}, {self.town_city}, {self.state}"

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('monitor', 'Monitor'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('assembled_cpu', 'Assembled CPU'),
        ('accessory', 'Accessory'),
    )

    productId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)  # New field for brand name
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stockLevel = models.PositiveIntegerField()
    description = models.TextField()
    main_image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.brand} - {self.name}"
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Additional image for {self.product.name}"

class Component(models.Model):
    componentId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)  # New field for brand name
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stockLevel = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='component_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.brand} - {self.name}"
        return f"{self.brand} - {self.name}"

class CustomPC(models.Model):
    configId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Custom PC {self.configId} for User {self.userId}"

class CustomPCComponent(models.Model):
    config = models.ForeignKey(CustomPC, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('config', 'component')

    def __str__(self):
        return f"Component {self.component} for Custom PC {self.config.configId}"

class Cart(models.Model):
    cartId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Cart {self.cartId} for {self.user.username}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s rating for {self.product.name}"