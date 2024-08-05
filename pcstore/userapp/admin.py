from django.contrib import admin

# Register your models here.
from .models import User,Address, Product

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Product)