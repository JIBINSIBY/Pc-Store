from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

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

class CustomPC(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # Default status to 'pending'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Custom PC {self.id} by {self.user.username}"

class CustomPCComponent(models.Model):
    custom_pc = models.ForeignKey(CustomPC, on_delete=models.CASCADE, related_name='components')
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    recommendedcomponent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('custom_pc', 'component')

    def __str__(self):
        return f"Component {self.component} for Custom PC {self.custom_pc.id}"

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

class CustomPCMessage(models.Model):
    custom_pc = models.ForeignKey('CustomPC', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_from_user = models.BooleanField(default=False)  # Added this field

    def __str__(self):
        return f"Message for CustomPC {self.custom_pc.id} by {self.sender.username}"

    class Meta:
        ordering = ['-created_at']

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True)  # Add this line

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

class CustomPCOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('building', 'Building'),
        ('shipped', 'Shipped'),
        ('enroute', 'En Route'),
        ('arrived', 'Arrived'),
    ]

    build = models.ForeignKey(CustomPC, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderComponent(models.Model):
    order = models.ForeignKey(CustomPCOrder, related_name='components', on_delete=models.CASCADE)
    component_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.component_name} for Order {self.order.id}"
