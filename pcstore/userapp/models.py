from django.contrib.auth.models import AbstractUser
from django.db import models

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
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stockLevel = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name