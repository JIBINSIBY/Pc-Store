from django.contrib import admin

# Register your models here.
from .models import User, Address, Product, Component, CustomPC, CustomPCComponent, ProductImage, Cart

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(Component)
admin.site.register(CustomPC)
admin.site.register(CustomPCComponent)
admin.site.register(ProductImage)
admin.site.register(Cart)