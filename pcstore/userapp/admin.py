from django.contrib import admin

# Register your models here.
from .models import User, Address, Product, Component, CustomPC, CustomPCComponent, ProductImage, OrderComponent, Cart, Rating,Order, OrderItem, CustomPCOrder, CustomPCMessage, DeliveryBoy, Delivery

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(Component)
admin.site.register(CustomPC)
admin.site.register(CustomPCComponent)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(Rating)
admin.site.register(CustomPCMessage)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CustomPCOrder)
admin.site.register(OrderComponent)
admin.site.register(DeliveryBoy)
admin.site.register(Delivery)