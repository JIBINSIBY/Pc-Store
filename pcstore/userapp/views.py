from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login,get_user_model,logout
from django.contrib import messages
# from .models import*
import re
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from .forms import UserUpdateForm
from .models import Address, Product, Component, ProductImage, Cart, Rating, CustomPC, CustomPCComponent,OrderComponent, CustomPCMessage, Order, OrderItem, CustomPCOrder
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from django.conf import settings
from django.db.models import Q, Avg, Sum
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
import logging
import math
from urllib.parse import unquote
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import CustomPCComponent, Component
import json
from django.shortcuts import render, redirect, get_object_or_404
import razorpay
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch
from django.contrib.auth.decorators import login_required
from .models import Order  # Import your Order model
from .models import DeliveryBoy
from .models import Delivery
from django.core.mail import send_mail
import random
import string
from django.http import JsonResponse
import json
from .models import Product
from openai import OpenAI
from django.http import JsonResponse
import json
from .models import Product # Import your models

logger = logging.getLogger(__name__)

user = get_user_model()
def index(request):
    latest_products = Product.objects.order_by('-productId')[:7]
    context = {
        'latest_products': latest_products
    }
    return render(request, 'index.html', context)

def mainpage(request):
    latest_monitors = Product.objects.filter(Q(category='monitor')).order_by('-productId')[:7]
    latest_keyboards = Product.objects.filter(category='keyboard').order_by('-productId')[:7]
    latest_assembledcpu = Product.objects.filter(category='assembled_cpu').order_by('-productId')[:7]
    latest_mice = Product.objects.filter(category='mouse').order_by('-productId')[:7]

    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()

    context = {
        'latest_monitors': latest_monitors,
        'latest_keyboards': latest_keyboards,
        'latest_assembledcpu': latest_assembledcpu,
        'latest_mice': latest_mice,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'main.html', context)

def signupu(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        hashed_password = make_password(password)
        if not email or not password or not cpassword:
            messages.error(request, 'All fields are required.')
            return render(request, 'signupuser.html')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, 'Enter a valid email address.')
            return render(request, 'signupuser.html')
        if password != cpassword:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signupuser.html')
        if user.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return render(request, 'signupuser.html')
        if password == cpassword:
            if user.objects.create(email=email,username=username, password=hashed_password):
                print(email)
                print(password)
                print(cpassword)
                messages.success(request, 'You have successfully registered! Please log in.')
                return redirect(reverse('loginu'))
    return render(request, 'signupuser.html')

def loginu(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        u = authenticate(request, email=email, password=password)
        if u is not None:
            login(request, u)
            request.session['user_id'] = u.id
            request.session['username'] = u.username
            request.session['user_role'] = u.role
            request.session.set_expiry(3600)  # Set session to expire in 1 hour
            request.session['last_activity'] = timezone.now().isoformat()
            redirect_url = reverse('userapp:mainpage')
            if u.role == 'admin':
                redirect_url = reverse('userapp:admin_dashboard')
            elif u.is_staff:
                redirect_url = reverse('userapp:staff_dashboard')
            elif u.role == 'delivery_boy':
                redirect_url = reverse('userapp:delivery_dashboard')
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid email or password'})
    return render(request, 'loginuser.html')

def forgotpassword(request):
    return render(request,'forgotpassword.html')

@login_required(login_url='userapp:login')
def profile(request):
    return render(request, 'profile.html')

def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.gender = request.POST.get('gender')
        user.email = request.POST.get('email')
        user.mobile = request.POST.get('mobile')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('userapp:profile')
    return render(request, 'profile_edit.html', {'user': request.user})

def address(request):
    user_addresses = Address.objects.filter(user=request.user)
    context = {
        'user_addresses': user_addresses,
    }
    return render(request, 'address.html', context)

def addaddress(request):
    if request.method == 'POST':
        # Extract data from POST request
        fullname = request.POST.get('fullname')
        mobile = request.POST.get('mobile')
        pincode = request.POST.get('pincode')
        flat_house = request.POST.get('flat_house')
        area_street = request.POST.get('area_street')
        town_city = request.POST.get('town_city')
        state = request.POST.get('state')
        landmark = request.POST.get('landmark')
        alternate_phone = request.POST.get('alternate_phone')

        # Create new Address object
        new_address = Address(
            user=request.user,
            fullname=fullname,
            mobile=mobile,
            pincode=pincode,
            flat_house=flat_house,
            area_street=area_street,
            town_city=town_city,
            state=state,
            landmark=landmark,
        )

        # Save the new address
        new_address.save()

        messages.success(request, 'Address added successfully!')
        return redirect(reverse('userapp:address'))

    return render(request, 'addaddress.html')

def editaddress(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        # Extract data from POST request
        address.fullname = request.POST.get('fullname')
        address.mobile = request.POST.get('mobile')
        address.pincode = request.POST.get('pincode')
        address.flat_house = request.POST.get('flat_house')
        address.area_street = request.POST.get('area_street')
        address.town_city = request.POST.get('town_city')
        address.state = request.POST.get('state')
        address.landmark = request.POST.get('landmark')
        
        # Save the updated address
        address.save()

        messages.success(request, 'Address updated successfully!')
        return redirect(reverse('userapp:address'))

    return render(request, 'editaddress.html', {'address': address})

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    response = redirect('userapp:index')  # Redirect to the index page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Address

@require_POST
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return JsonResponse({'success': True})

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


from django.contrib.auth.decorators import login_required

@login_required(login_url='userapp:index')
def admin_dashboard(request):
    # Calculate today's sales
    #today = timezone.now().date()
    #today_sales = Order.objects.filter(order_date__date=today).aggregate(
    #    total_sales=Sum('total_amount'),
    #    total_orders=Count('id'),
    #    products_sold=Sum('orderitem__quantity'),
    #    new_customers=Count('user', distinct=True)
    #)

    # Calculate yesterday's sales for comparison
    #yesterday = today - timedelta(days=1)
    #yesterday_sales = Order.objects.filter(order_date__date=yesterday).aggregate(
    #    total_sales=Sum('total_amount'),
    #    total_orders=Count('id'),
    #    products_sold=Sum('orderitem__quantity'),
    #    new_customers=Count('user', distinct=True)
    #)

    # Calculate percentage changes
    #sales_change = calculate_percentage_change(today_sales['total_sales'], yesterday_sales['total_sales'])
    #orders_change = calculate_percentage_change(today_sales['total_orders'], yesterday_sales['total_orders'])
    #products_change = calculate_percentage_change(today_sales['products_sold'], yesterday_sales['products_sold'])
    #customers_change = calculate_percentage_change(today_sales['new_customers'], yesterday_sales['new_customers'])

    # Get out of stock products
    out_of_stock_products = Product.objects.filter(stockLevel=0)

    context = {
        #'today_sales': today_sales,
        #'sales_change': sales_change,
        #'orders_change': orders_change,
        #'products_change': products_change,
        #'customers_change': customers_change,
        'out_of_stock_products': out_of_stock_products,
    }
    return render(request, 'adminmain.html', context)

#def calculate_percentage_change(today_value, yesterday_value):
#    if yesterday_value and yesterday_value != 0:
#        return ((today_value or 0) - yesterday_value) / yesterday_value * 100
 #   return 0

from django.contrib.auth.decorators import login_required

@login_required(login_url='userapp:login')
def admin_profile(request):
    return render(request, 'admin_profile.html', {'user': request.user})

@login_required(login_url='userapp:login')
def update_admin_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.mobile = request.POST.get('mobile')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('userapp:admin_profile')
    return render(request, 'update_admin_profile.html', {'user': request.user})

@login_required(login_url='userapp:login')
def admin_userview(request):
    User = get_user_model()
    users = User.objects.exclude(is_superuser=True)
    return render(request, 'admin_userview.html', {'users': users})



@login_required
@require_POST
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def change_user_role(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        new_role = data.get('role')
        
        if new_role not in ['user', 'staff', 'delivery_boy']:
            return JsonResponse({'success': False, 'error': 'Invalid role'}, status=400)
        
        user = User.objects.get(id=user_id)
        
        # Reset all role flags
        user.is_staff = False
        user.is_deliveryboy = False
        
        # Set appropriate flags based on role
        if new_role == 'staff':
            user.is_staff = True
        elif new_role == 'delivery_boy':
            user.is_deliveryboy = True
        
        # Update the role field
        user.role = new_role
        user.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='userapp:login')
def admin_productadd(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        brand = request.POST.get('brand_name')  # Get the brand name from the form
        category = request.POST.get('category')
        price = request.POST.get('price')
        stockLevel = request.POST.get('stockLevel')
        description = request.POST.get('description')
        main_image = request.FILES.get('main_image')
        additional_images = request.FILES.getlist('additional_images')

        product = Product(
            name=name,
            brand=brand,  # Add the brand to the Product instance
            category=category,
            price=price,
            stockLevel=stockLevel,
            description=description,
            main_image=main_image
        )
        product.save()

        for image in additional_images:
            ProductImage.objects.create(product=product, image=image)

        messages.success(request, 'Product added successfully!')
        return redirect('userapp:admin_productadd')

    return render(request, 'admin_productadd.html')

@login_required(login_url='userapp:login')
def admin_viewproduct(request):
    products = Product.objects.all()
    return render(request, 'admin_viewproduct.html', {'products': products})

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)

@require_POST
def delete_product(request, product_id):
    logger.info(f"Attempting to delete product with ID: {product_id}")
    try:
        product = Product.objects.get(productId=product_id)
        product.delete()
        logger.info(f"Product with ID {product_id} deleted successfully")
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        logger.error(f"Product with ID {product_id} not found")
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    except Exception as e:
        logger.error(f"Error deleting product with ID {product_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
 
@login_required(login_url='userapp:login')   
def admin_editproduct(request, product_id):
    print(f"Attempting to edit product with ID: {product_id}")  # Add this line
    product = get_object_or_404(Product, productId=product_id)
    additional_images = ProductImage.objects.filter(product=product)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.stockLevel = request.POST.get('stockLevel')
        product.description = request.POST.get('description')
        
        if 'main_image' in request.FILES:
            product.main_image = request.FILES['main_image']
        
        product.save()

        # Handle additional images
        additional_images = request.FILES.getlist('additional_images')
        for image in additional_images:
            ProductImage.objects.create(product=product, image=image)

        messages.success(request, 'Product updated successfully!')
        return redirect('userapp:admin_viewproduct')

    context = {
        'product': product,
        'additional_images': additional_images,
        'product_id': product_id,
    }
    return render(request, 'admin_editproduct.html', context)

@login_required(login_url='userapp:login')
def admin_editcomponent(request, component_id):
    component = get_object_or_404(Component, componentId=component_id)
    # ... rest of the function ...
    return render(request, 'admin_editcomponent.html', {'component': component})

@login_required(login_url='userapp:login')
def admin_viewcomponent(request):
    components = Component.objects.all()
    return render(request, 'admin_viewcomponent.html', {'components': components})

@login_required(login_url='userapp:login')
def admin_editcomponent(request, component_id):
    print(f"Editing component with ID: {component_id}")  # Debug print
    component = get_object_or_404(Component, componentId=component_id)
    if request.method == 'POST':
        component.name = request.POST.get('name')
        component.brand = request.POST.get('brand')
        component.category = request.POST.get('category')
        component.price = request.POST.get('price')
        component.stockLevel = request.POST.get('stockLevel')
        component.description = request.POST.get('description')
        
        if 'image' in request.FILES:
            component.image = request.FILES['image']
        
        component.save()
        messages.success(request, 'Component updated successfully!')
        return redirect('userapp:admin_viewcomponent')
    
    return render(request, 'admin_editcomponent.html', {'component': component})

import traceback

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def delete_component(request, component_id):
    logger.info(f"Attempting to delete component with ID: {component_id}")
    try:
        component = Component.objects.get(componentId=component_id)
        component_name = component.name  # Store the name for logging
        component.delete()
        logger.info(f"Successfully deleted Component '{component_name}' with ID: {component_id}")
        return JsonResponse({'success': True, 'message': f'Component {component_name} deleted successfully'})
    except Component.DoesNotExist:
        logger.error(f"Component with ID {component_id} not found")
        return JsonResponse({'success': False, 'error': 'Component not found'}, status=404)
    except Exception as e:
        logger.error(f"Error deleting Component with ID {component_id}: {str(e)}")
        logger.error(traceback.format_exc())  # Log the full traceback
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='userapp:login')
def admin_addcomponent(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        category = request.POST.get('category')
        price = request.POST.get('price')
        stockLevel = request.POST.get('stockLevel')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        component = Component(
            name=name,
            brand=brand,
            category=category,
            price=price,
            stockLevel=stockLevel,
            description=description,
            image=image
        )
        component.save()
        messages.success(request, 'Component added successfully!')
        return redirect('userapp:admin_addcomponent')

    return render(request, 'admin_addcomponent.html')

def search_results(request):
    query = request.GET.get('q')
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )
    else:
        results = []
    return render(request, 'search_results.html', {'results': results, 'query': query})
@login_required(login_url='userapp:login')
def pc_custom(request):
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
        
    context = {
        'has_new_messages': has_new_messages,
    }
    return render(request, 'pc_custom.html', context)


@login_required(login_url='userapp:login')
def keyboards_view(request):
    keyboards = Product.objects.filter(category='keyboard')
    available_brands = keyboards.values_list('brand', flat=True).distinct()
    
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
        
    context = {
        'keyboards': keyboards,
        'available_brands': available_brands,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'keyboards.html', context)

@login_required(login_url='userapp:login')
def mouses_view(request):
    mouses = Product.objects.filter(category='mouse')
    available_brands = mouses.values_list('brand', flat=True).distinct()
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
    context = {
        'mouses': mouses,
        'available_brands': available_brands,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'mouse.html', context)

@login_required(login_url='userapp:login')
def monitors_view(request):
    monitors = Product.objects.filter(category='monitor')
    available_brands = monitors.values_list('brand', flat=True).distinct()
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
    context = {
        'monitors': monitors,
        'available_brands': available_brands,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'monitors.html', context)

@login_required(login_url='userapp:login')
def assembledcpus_view(request):
    assembledcpus = Product.objects.filter(category='assembled_cpu')
    available_brands = assembledcpus.values_list('brand', flat=True).distinct()
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
    context = {
        'assembledcpus': assembledcpus,
        'available_brands': available_brands,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'assembled_cpu.html', context)

@login_required(login_url='userapp:login')
def accessories_view(request):
    accessories = Product.objects.filter(category='accessory')
    available_brands = accessories.values_list('brand', flat=True).distinct()
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
    context = {
        'accessories': accessories,
        'available_brands': available_brands,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'accessory.html', context)






@require_POST
@require_POST
def delete_additional_image(request, image_id):
    try:
        image = ProductImage.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'success': True})
    except ProductImage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product

from django.db.models import Avg

def single_product(request, product_id, category):
    product = get_object_or_404(Product, productId=product_id)
    average_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    ratings = Rating.objects.filter(product=product).order_by('-created_at')
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, product=product).first()
    
    context = {
        'product': product,
        'category': category,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'ratings': ratings,
    }
    return render(request, 'singleproduct.html', context)
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        return render(request, 'cartview.html', {'cart_items': []})

    total_price = sum(item.totalPrice for item in cart_items)
    total_discount = 0  # Calculate this based on your discount logic
    delivery_charges = 174  # You can adjust this or make it dynamic
    total_amount = total_price - total_discount + delivery_charges
    total_savings = total_discount

    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'delivery_charges': delivery_charges,
        'total_amount': total_amount,
        'total_savings': total_savings,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'cartview.html', context)



from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cart, Product

@require_POST
@csrf_exempt
def add_to_cart(request):
    data = json.loads(request.body)
    product_id = data.get('productId')
    quantity = data.get('quantity', 1)

    try:
        product = Product.objects.get(productId=product_id)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 0, 'totalPrice': 0}
        )

        total_quantity = cart_item.quantity + quantity
        if total_quantity > product.stockLevel:
            return JsonResponse({'success': False, 'error': 'Out of stock', 'available': product.stockLevel})

        cart_item.quantity = total_quantity
        cart_item.totalPrice = total_quantity * product.price
        cart_item.save()

        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def remove_from_cart(request):
    data = json.loads(request.body)
    product_id = data.get('productId')

    try:
        cart_item = Cart.objects.get(user=request.user, product__productId=product_id)
        cart_item.delete()

        # Recalculate cart totals
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.totalPrice for item in cart_items)
        total_discount = 0  # Calculate this based on your discount logic
        delivery_charges = 174  # You can adjust this or make it dynamic
        total_amount = total_price - total_discount + delivery_charges
        total_savings = total_discount

        return JsonResponse({
            'success': True,
            'cart_items_count': cart_items.count(),
            'total_price': total_price,
            'total_discount': total_discount,
            'delivery_charges': delivery_charges,
            'total_amount': total_amount,
            'total_savings': total_savings,
        })
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found in cart'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def update_cart_quantity(request):
    data = json.loads(request.body)
    product_id = data.get('productId')
    new_quantity = data.get('quantity')

    try:
        cart_item = Cart.objects.get(user=request.user, product__productId=product_id)
        product = cart_item.product

        if new_quantity > product.stockLevel:
            return JsonResponse({'success': False, 'error': f'Maximum available quantity is {product.stockLevel}'})

        if new_quantity < 1:
            return JsonResponse({'success': False, 'error': 'Minimum quantity is 1'})

        cart_item.quantity = new_quantity
        cart_item.totalPrice = new_quantity * product.price
        cart_item.save()

        # Recalculate cart totals
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.totalPrice for item in cart_items)
        total_discount = 0  # Calculate this based on your discount logic
        delivery_charges = 174  # You can adjust this or make it dynamic
        total_amount = total_price - total_discount + delivery_charges
        total_savings = total_discount

        return JsonResponse({
            'success': True,
            'cart_items_count': cart_items.count(),
            'total_price': total_price,
            'total_discount': total_discount,
            'delivery_charges': delivery_charges,
            'total_amount': total_amount,
            'total_savings': total_savings,
        })
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found in cart'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
     
@require_POST
def remove_main_image(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    if product.main_image:
        # Delete the file from storage
        default_storage.delete(product.main_image.path)
        # Clear the main_image field
        product.main_image = None
        product.save()
    return JsonResponse({'success': True})

@require_POST
def remove_additional_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    if image.image:
        # Delete the file from storage
        default_storage.delete(image.image.path)
    # Delete the database record
    image.delete()
    return JsonResponse({'success': True})

def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) > 1:
        suggestions = Product.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        ).values('name', 'productId', 'category')[:5]
        return JsonResponse(list(suggestions), safe=False)
    return JsonResponse([], safe=False)

def check_session(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if timezone.now() - last_activity > timedelta(hours=1):
                    logout(request)
                    return redirect('userapp:login')  # Replace with your login URL name
            request.session['last_activity'] = timezone.now().isoformat()
        return self.get_response(request)

@require_POST
def add_address(request):
    user = request.user
    address = Address.objects.create(
        user=user,
        full_name=request.POST.get('full_name'),
        mobile_number=request.POST.get('mobile_number'),
        pincode=request.POST.get('pincode'),
        flat_house=request.POST.get('flat_house'),
        area_street=request.POST.get('area_street'),
        town_city=request.POST.get('town_city'),
        state=request.POST.get('state'),
        landmark=request.POST.get('landmark'),
        country='India'  # Assuming the country is always India
    )
    return JsonResponse({
        'success': True,
        'address': {
            'id': address.id,
            'full_name': address.full_name,
            'mobile_number': address.mobile_number,
            'pincode': address.pincode,
            'flat_house': address.flat_house,
            'area_street': address.area_street,
            'town_city': address.town_city,
            'state': address.state,
            'landmark': address.landmark,
            'country': address.country
        }
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, productId=product_id)
    
    # Calculate average rating and count of ratings for this product
    rating_data = Rating.objects.filter(product=product).aggregate(
        average_rating=Avg('rating'),
        rating_count=Count('rating')
    )
    
    average_rating = rating_data['average_rating'] or 0
    average_rating = round(average_rating, 1)  # Round to one decimal place
    rating_count = rating_data['rating_count'] or 0
    
    # Get all ratings for this product
    ratings = Rating.objects.filter(product=product).order_by('-created_at')
    
    context = {
        'product': product,
        'ratings': ratings,
        'average_rating': average_rating,
        'rating_count': rating_count,
    }
    return render(request, 'singleproduct.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Rating
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

@login_required
@require_POST
def add_rating(request, product_id):
    try:
        product = Product.objects.get(productId=product_id)
        rating_value = int(request.POST['rating'])
        description = request.POST['description']
        
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'rating': rating_value, 'description': description}
        )
        
        return JsonResponse({'success': True, 'message': 'Rating and review successfully submitted.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from userapp.models import User  # Import your User model

login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    user_addresses = Address.objects.filter(user=user)
    total_price = sum(item.totalPrice for item in cart_items)
    total_discount = 0  # Calculate this based on your discount logic
    delivery_charges = 174  # You can adjust this or make it dynamic
    total_amount = total_price - total_discount + delivery_charges
    total_savings = total_discount
    
    # Get the Razorpay key ID from settings
    razorpay_key_id = settings.RAZORPAY_KEY_ID

    context = {
        'user': user,
        'cart_items': cart_items,
        'user_addresses': user_addresses,
        'total_price': total_price,
        'total_discount': total_discount,
        'delivery_charges': delivery_charges,
        'total_amount': total_amount,
        'total_savings': total_savings,
        'razorpay_key_id': razorpay_key_id,  # Add Razorpay key ID to context
    }
    
    return render(request, 'checkout.html', context)

    from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

def logout_and_redirect(request):
    logout(request)
    return redirect(reverse('userapp:login'))

def upi_payment(request):
    # Handle UPI payment logic
    return render(request, 'upi_payment.html')

def card_payment(request):
    # Handle card payment logic
    return render(request, 'card_payment.html')

def cod_confirmation(request):
    # Handle Cash on Delivery confirmation
    return render(request, 'cod_confirmation.html')

import logging
from django.http import JsonResponse
from .models import Component

logger = logging.getLogger(__name__)
@login_required(login_url='userapp:login')
def get_components(request):
    category = request.GET.get('category', '')
    logger.info(f"Fetching components for category: {category}")
    
    category_mapping = {
        'ram': 'RAM',
        'hard drive': 'Hard drive',
        'case': 'Case',
        'power supply unit': 'Power supply unit',
        'graphics card': 'Graphics card',
        'cpu cooler': 'CPU Cooler',
        'wifi card': 'Wifi card',
        'bluetooth card': 'Bluetooth card',
        'motherboard': 'Motherboard',
        'cpu': 'CPU/processor'
    }
    
    db_category = category_mapping.get(category.lower(), category)
    logger.info(f"Mapped category: {db_category}")
    
    if db_category:
        components = Component.objects.filter(category__iexact=db_category)
    else:
        components = Component.objects.all()
    
    logger.info(f"Found {components.count()} components")
    
    data = [{
        'componentId': c.componentId,
        'name': c.name,
        'price': str(c.price),
        'image': c.image.url if c.image else '',
        'category': c.category,
        'brand': c.brand,
        'description': c.description
    } for c in components]
    
    logger.info(f"Returning {len(data)} components")
    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import CustomPC, CustomPCComponent, Component
import json

@login_required
@csrf_exempt
def check_compatibility(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            components = data.get('components', [])
            total_price = data.get('totalPrice', 0)
            
            # Log received data
            logger.info(f"Received data: {data}")

            # Create a new CustomPC instance
            custom_pc = CustomPC.objects.create(
                user=request.user,
                total_price=total_price,
                status='Pending'
            )

            # Create CustomPCComponent instances for each component
            for component in components:
                CustomPCComponent.objects.create(
                    custom_pc=custom_pc,
                    component_id=component['componentId'],
                    quantity=component['quantity']
                )

            return JsonResponse({'success': True, 'message': 'Configuration submitted successfully'})
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except KeyError as e:
            logger.error(f"Key Error: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Missing required field: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in check_compatibility: {str(e)}")
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred'}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
import os

import logging

logger = logging.getLogger(__name__)

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

@login_required
@csrf_exempt
def generate_pdf(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            components = data.get('components', [])
            total_price = data.get('totalPrice', 0)
            full_name = data.get('fullName', '')

            logger.info(f"Generating PDF for user: {full_name}")

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            elements = []

            # Add logo
            logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo3.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=2*inch, height=1*inch)
                elements.append(logo)
            else:
                logger.warning(f"Logo file not found at {logo_path}")

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, spaceAfter=12, alignment=TA_CENTER)
            normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=12, spaceAfter=6)
            highlight_style = ParagraphStyle('Highlight', parent=styles['Normal'], fontSize=14, textColor=colors.red, fontName='Helvetica-Bold')
            footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)

            # Title and introduction
            elements.append(Paragraph("Custom PC Build Specification", title_style))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"Customer: {full_name}", normal_style))
            elements.append(Paragraph("Total Price: ", normal_style))
            elements.append(Paragraph(f"${total_price:.2f}", highlight_style))
            elements.append(Spacer(1, 0.2*inch))

            # Components table
            data = [['Category', 'Component', 'Brand', 'Price', 'Quantity', 'Total']]
            for component in components:
                data.append([
                    component['category'],
                    component['name'],
                    component['brand'],
                    f"${float(component['price']):.2f}",
                    component['quantity'],
                    f"${float(component['price']) * component['quantity']:.2f}"
                ])

            # Set a fixed table width (adjust as needed)
            table_width = 7.5 * inch  # 7.5 inches wide (letter page is 8.5 inches wide)
            
            # Calculate column widths as a percentage of the table width
            col_widths = [
                table_width * 0.15,  # Category
                table_width * 0.25,  # Component
                table_width * 0.15,  # Brand
                table_width * 0.15,  # Price
                table_width * 0.15,  # Quantity
                table_width * 0.15   # Total
            ]

            table = Table(data, colWidths=col_widths)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E8F5E9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#F1F8E9')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ])
            table.setStyle(style)

            # Center the table on the page
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Table([[table]], colWidths=[letter[0]], style=[('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

            # Add some space before the footer
            elements.append(Spacer(1, 1*inch))

            # Footer with copyright and contact information
            footer_text = f"""
            © {timezone.now().year} Your Company Name. All rights reserved.
            Contact us: email@example.com | Phone: +1 (123) 456-7890
            Website: www.yourcompany.com
            """
            footer = Paragraph(footer_text, footer_style)
            elements.append(footer)

            doc.build(elements)
            buffer.seek(0)
            logger.info("PDF generated successfully")
            
            # Set the appropriate headers for PDF download
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="custom_pc_build.pdf"'
            return response

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponse("Invalid request method", status=400)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomPC, CustomPCComponent

@login_required
def yourbuild(request):
    # Fetch all custom PCs for the logged-in user, excluding paid ones
    builds = CustomPC.objects.filter(user=request.user).exclude(custompcorder__status='paid').order_by('-created_at')
    
    # Count new messages
    
    # Prepare data for the template
    builds_data = []
    for pc in builds:
        components = CustomPCComponent.objects.filter(custom_pc=pc)
        builds_data.append({
            'id': pc.id,
            'status': pc.status,
            'created_at': pc.created_at,
            'components': components
        })
    has_new_messages = False
    if request.user.is_authenticated:
        has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
    context = {
        'builds': builds_data,
        'has_new_messages': has_new_messages,
    }
    return render(request, 'yourbuild.html', context)

@login_required
def build_components(request, build_id):
    try:
        custom_pc = CustomPC.objects.get(id=build_id, user=request.user)
        components = CustomPCComponent.objects.filter(custom_pc=custom_pc)
        data = {
            'components': [
                {
                    'category': component.component.category,
                    'name': component.component.name,
                    'quantity': component.quantity,  # Include quantity
                    'price': float(component.component.price)  # Include price if available
                } for component in components
            ]
        }
        return JsonResponse(data)
    except CustomPC.DoesNotExist:
        return JsonResponse({'error': 'Build not found'}, status=404)

from django.contrib.auth.decorators import login_required, user_passes_test


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomPC

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def staff_build_requests(request):
    build_requests = CustomPC.objects.select_related('user').all()
    
    # Sorting
    sort = request.GET.get('sort', 'latest')
    if sort == 'oldest':
        build_requests = build_requests.order_by('created_at')
    else:  # default to latest
        build_requests = build_requests.order_by('-created_at')
    
    # Status filtering
    status = request.GET.get('status')
    if status:
        build_requests = build_requests.filter(status=status)
        print(f"Filtering by status: {status}, found {build_requests.count()} requests")
    
    context = {'build_requests': build_requests}
    return render(request, 'staff_build_requests.html', context)

@login_required
@user_passes_test(is_staff)
def build_request_details(request, build_id):
    build = get_object_or_404(CustomPC, id=build_id)
    components = CustomPCComponent.objects.filter(custom_pc=build).select_related('component')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        message = request.POST.get('message')
        if new_status:
            build.status = new_status
            build.save()
        if message:
            # Here you would typically save the message to a Message model
            # For simplicity, we'll just pass it back in the context
            pass
    
    context = {
        'build': build,
        'components': [
            {
                'id': comp.id,
                'name': comp.component.name,
                'category': comp.component.category,
                'quantity': comp.quantity,
                'recommendedcomponent': comp.recommendedcomponent,
                'recommended_details': get_recommended_component_details(comp.recommendedcomponent) if comp.recommendedcomponent else None
            } for comp in components
        ],
        'message': message if 'message' in locals() else None
    }
    return render(request, 'build_request_details.html', context)

def get_recommended_component_details(component_name):
    try:
        component = Component.objects.get(name=component_name)
        return {
            'name': component.name,
            'category': component.category,
            'price': str(component.price),
            'description': component.description,
            'image_url': component.image.url if component.image else None,
        }
    except Component.DoesNotExist:
        return None

@csrf_exempt
@require_POST
def update_build_status(request, build_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        logger.info(f"Attempting to update build {build_id} to status {new_status}")
        
        if not new_status:
            logger.error("No status provided")
            return JsonResponse({'success': False, 'error': 'No status provided'}, status=400)

        custom_pc = CustomPC.objects.get(id=build_id)
        logger.info(f"Current status: {custom_pc.status}")
        custom_pc.status = new_status
        custom_pc.save()
        logger.info(f"Status updated to: {custom_pc.status}")

        # Refresh from database to ensure we're getting the updated value
        custom_pc.refresh_from_db()
        logger.info(f"Status after refresh: {custom_pc.status}")

        # Get components using the correct relationship
        components = custom_pc.components.all()  # Use the related name here

        return JsonResponse({
            'success': True, 
            'message': 'Status updated successfully',
            'new_status': custom_pc.status,
            'components': [{'name': comp.name, 'quantity': comp.quantity} for comp in components]
        })
    except CustomPC.DoesNotExist:
        logger.error(f"CustomPC with id {build_id} not found")
        return JsonResponse({'success': False, 'error': f'Custom PC build with id {build_id} not found'}, status=404)
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    # Add any context data needed for the staff dashboard
    context = {}
    return render(request, 'staff_dashboard.html', context)

from django.http import JsonResponse
from .models import Component

def component_details_by_name(request, component_name):
    try:
        component = Component.objects.get(name=component_name)
        data = {
            'name': component.name,
            'category': component.category,
            'description': component.description,
            'price': component.price,
        }
        return JsonResponse(data)
    except Component.DoesNotExist:
        return JsonResponse({'error': 'Component not found'}, status=404)
    
logger = logging.getLogger(__name__)

def get_component_category(request, component_name):
    logger.info(f"Fetching category for component: {component_name}")
    try:
        component = Component.objects.filter(name=component_name).first()
        if component:
            logger.info(f"Category for {component_name}: {component.category}")
            return JsonResponse({'category': component.category})
        else:
            logger.error(f"Component not found: {component_name}")
            return JsonResponse({'error': 'Component not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching category for {component_name}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def get_recommended_components(request, category):
    category = unquote(category)  # Decode URL-encoded category
    logger.info(f"Fetching recommended components for category: {category}")
    try:
        components = Component.objects.filter(category=category)[:10]
        data = [{
            'id': c.componentId,
            'name': c.name,
            'price': str(c.price),
            'description': c.description if hasattr(c, 'description') else '',
            'image_url': f'/media/component_images/{os.path.basename(c.image.name)}' if c.image else None
        } for c in components]
        logger.info(f"Found {len(data)} recommended components for {category}")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Error fetching recommended components for {category}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
from django.views.decorators.csrf import csrf_protect    
@csrf_protect
@require_POST
def add_recommended_component(request):
    try:
        data = json.loads(request.body)
        custom_pc_component_id = data.get('custom_pc_component_id')
        recommended_component_name = data.get('recommended_component_name')

        logger.info(f"Attempting to add recommended component. CustomPCComponent ID: {custom_pc_component_id}, Recommended Component Name: {recommended_component_name}")

        custom_pc_component = CustomPCComponent.objects.get(id=custom_pc_component_id)
        recommended_component = Component.objects.get(name=recommended_component_name)

        # Update the recommendedcomponent field with the component name
        custom_pc_component.recommendedcomponent = recommended_component_name
        custom_pc_component.save()

        logger.info(f"Successfully added recommended component {recommended_component_name} to CustomPCComponent {custom_pc_component}")

        # Prepare the response data
        response_data = {
            'status': 'success',
            'message': 'Recommended component added successfully',
            'recommended_component': {
                'name': recommended_component.name,
                'category': recommended_component.category,
                'price': str(recommended_component.price),
                'description': recommended_component.description,
                'image_url': recommended_component.image.url if recommended_component.image else None,
            }
        }

        return JsonResponse(response_data)
    except CustomPCComponent.DoesNotExist:
        logger.error(f"CustomPCComponent with ID {custom_pc_component_id} not found")
        return JsonResponse({'status': 'error', 'message': 'Custom PC Component not found'}, status=404)
    except Component.DoesNotExist:
        logger.error(f"Component with name {recommended_component_name} not found")
        return JsonResponse({'status': 'error', 'message': 'Recommended Component not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding recommended component: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@require_POST
@csrf_protect
def send_message(request, build_id):
    try:
        data = json.loads(request.body)
        message_text = data.get('message')
        
        build = CustomPC.objects.get(id=build_id)
        
        message = CustomPCMessage.objects.create(
            custom_pc=build,
            sender=request.user,
            message=message_text
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'text': message.message,
                'sender': message.sender.username,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except CustomPC.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Build not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def messageforbuild(request):
    builds = CustomPC.objects.filter(user=request.user)
    
    build_data = []
    for build in builds:
        messages = CustomPCMessage.objects.filter(custom_pc=build).order_by('-created_at')
        
        # Mark all messages as read
        messages.update(is_read=True)
        
        build_data.append({
            'build': build,
            'messages': messages
        })
    
    # Check for new messages
    has_new_messages = CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).exists()
    
    context = {
        'build_data': build_data,
        'has_new_messages': has_new_messages,
    }
    
    return render(request, 'messageforbuild.html', context)
def get_recommendations(request, build_id):
    build = get_object_or_404(CustomPC, id=build_id, user=request.user)
    components = CustomPCComponent.objects.filter(custom_pc=build)
    
    recommendations = []
    for component in components:
        if component.recommendedcomponent:
            recommendations.append({
                'component_type': component.component.category if component.component else 'Unknown',
                'name': component.recommendedcomponent
            })
    
    return JsonResponse({'recommendations': recommendations})
    
@require_POST
def user_send_message_to_staff(request):
    build_id = request.POST.get('build_id')
    message_text = request.POST.get('message')

    try:
        build = CustomPC.objects.get(id=build_id, user=request.user)
        message = CustomPCMessage.objects.create(
            custom_pc=build,
            sender=request.user,
            message=message_text,
            is_from_user=True  # Assuming you have this field to distinguish user messages
        )
        return JsonResponse({'status': 'success', 'message': 'Message sent successfully to staff'})
    except CustomPC.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Build not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
from django.db import transaction
@require_POST
@transaction.atomic
def accept_recommendations(request):
    build_id = request.POST.get('build_id')

    try:
        build = CustomPC.objects.get(id=build_id, user=request.user)
        components = CustomPCComponent.objects.filter(custom_pc=build)

        changes_made = False
        for component in components:
            if component.recommendedcomponent:
                recommended_parts = component.recommendedcomponent.split('|')
                recommended_name = recommended_parts[0].strip()
                recommended_quantity = recommended_parts[1].strip() if len(recommended_parts) > 1 else '1'
                
                try:
                    recommended_component = Component.objects.get(name=recommended_name)
                    component.component_id = recommended_component.componentId
                    if recommended_quantity.isdigit():
                        component.quantity = int(recommended_quantity)
                    component.recommendedcomponent = None
                    component.save()
                    changes_made = True
                except Component.DoesNotExist:
                    print(f"Recommended component not found: {recommended_name}")

        if changes_made:
            CustomPCMessage.objects.create(
                custom_pc=build,
                sender=request.user,
                message="The user has accepted the recommended changes.",
                is_from_user=True
            )
            return JsonResponse({'status': 'success', 'message': 'Recommendations accepted successfully'})
        else:
            return JsonResponse({'status': 'info', 'message': 'No valid recommendations to apply'})

    except CustomPC.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Build not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def checkoutcustom(request, build_id):
    build = get_object_or_404(CustomPC, id=build_id, user=request.user)
    custom_components = CustomPCComponent.objects.filter(custom_pc=build)
    
    components_with_prices = []
    total_price = 0
    
    for custom_component in custom_components:
        component = custom_component.component
        quantity = custom_component.quantity
        price = component.price * quantity
        total_price += price
        
        components_with_prices.append({
            'name': component.name,
            'quantity': quantity,
            'price': price,
            'unit_price': component.price
        })
    
    # Update the total_price of the CustomPC object
    build.total_price = total_price
    build.save()
    
    # Fetch addresses for the current user
    user_addresses = Address.objects.filter(user=request.user)
    
    context = {
        'custom_pc': build,
        'components': components_with_prices,
        'total_price': total_price,
        'user': request.user,
        'user_addresses': user_addresses,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    
    return render(request, 'checkoutcustombuild.html', context)

import razorpay
@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency', 'INR')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        try:
            order = client.order.create({'amount': amount, 'currency': currency, 'payment_capture': '1'})
            return JsonResponse({'id': order['id'], 'amount': order['amount'], 'currency': order['currency']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def your_view_function(request):
    # ... existing code ...

    # Check for new messages
    has_new_messages = CustomPCMessage.objects.filter(is_read=False, user=request.user).exists()

    context = {
        # ... other context variables ...
        'has_new_messages': has_new_messages,
    }

    return render(request, 'main.html', context)


@require_POST
def mark_messages_read(request):
    if request.user.is_authenticated:
        CustomPCMessage.objects.filter(custom_pc__user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=403)

@require_POST
def remove_build(request, build_id):
    try:
        build = CustomPC.objects.get(id=build_id, user=request.user)
        
        # Remove associated components
        CustomPCComponent.objects.filter(custom_pc=build).delete()
        
        # Remove the build itself
        build.delete()
        
        return JsonResponse({'success': True})
    except CustomPC.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Build not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import CustomPC
import json
import razorpay

import logging
import json
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomPC

logger = logging.getLogger(__name__)

@csrf_exempt
def create_custom_order(request):
    logger.info(f"Razorpay Key ID: {settings.RAZORPAY_KEY_ID[:5]}...")
    logger.info(f"Razorpay Key Secret: {settings.RAZORPAY_SECRET[:5]}...")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            build_id = data.get('build_id')
            logger.info(f"Received request to create order for build_id: {build_id}")

            build = CustomPC.objects.get(id=build_id, user=request.user)
            amount = int(build.total_price * 100)  # Convert to paise
            logger.info(f"Build total price: {build.total_price}, Amount in paise: {amount}")

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
            
            payment_data = {
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'
            }
            logger.info(f"Attempting to create Razorpay order with data: {payment_data}")
            
            order = client.order.create(data=payment_data)
            logger.info(f"Razorpay order created successfully: {order}")
            
            return JsonResponse({
                'order_id': order['id'],
                'amount': amount,
            })
        except CustomPC.DoesNotExist:
            logger.error(f"CustomPC with id {build_id} not found for user {request.user}")
            return JsonResponse({'error': 'Custom PC build not found'}, status=404)
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@transaction.atomic
def payment_success(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            razorpay_order_id = data.get('order_id')
            signature = data.get('signature')

            # Verify the payment with Razorpay (implement this function)
            # if not verify_razorpay_payment(payment_id, razorpay_order_id, signature):
            #     return JsonResponse({'success': False, 'message': 'Invalid payment'})

            user = request.user
            cart_items = Cart.objects.filter(user=user)

            if not cart_items.exists():
                return JsonResponse({'success': False, 'message': 'Cart is empty'})

            # Calculate total amount
            total_amount = sum(item.totalPrice for item in cart_items)

            # Create a new order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                payment_id=payment_id,
                razorpay_order_id=razorpay_order_id,
                status='Paid'
            )

            # Add cart items to the order and update product stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                product = cart_item.product
                product.stockLevel = max(0, product.stockLevel - cart_item.quantity)
                product.save()

            # Clear the user's cart
            cart_items.delete()

            return JsonResponse({'success': True, 'order_id': order.id})
        except Exception as e:
            # If any error occurs, rollback the transaction
            transaction.set_rollback(True)
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})


@csrf_exempt
def create_razorpay_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            build_id = data.get('build_id')
            address_id = data.get('address_id')
            amount = data.get('amount')

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(float(amount) * 100),  # Razorpay expects amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })

            return JsonResponse({
                'order_id': razorpay_order['id'],
                'amount': amount
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import CustomPC, CustomPCOrder, Address, OrderComponent, CustomPCComponent

logger = logging.getLogger(__name__)

@csrf_exempt
@transaction.atomic
def payment_success_custom_pc(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            order_id = data.get('order_id')
            build_id = data.get('build_id')
            address_id = data.get('address_id')

            # TODO: Verify the payment signature here (implementation depends on your Razorpay setup)

            # Retrieve the CustomPC instance
            custom_pc = CustomPC.objects.get(id=build_id, user=request.user)
            address = Address.objects.get(id=address_id, user=request.user)

            # Create CustomPCOrder without the signature field
            custom_pc_order = CustomPCOrder.objects.create(
                user=request.user,
                total_price=custom_pc.total_price,
                payment_id=payment_id,
                razorpay_order_id=order_id,
                address=address,
                status='paid'  # Set the status to 'paid'
            )

            # Add components to the order
            for pc_component in CustomPCComponent.objects.filter(custom_pc=custom_pc):
                OrderComponent.objects.create(
                    order=custom_pc_order,
                    component_name=pc_component.component.name,  # Assuming you have a way to get the component name
                    brand=pc_component.component.brand,  # Assuming you have a way to get the component brand
                    category=pc_component.component.category,  # Assuming you have a way to get the component category
                    price=pc_component.component.price,  # Assuming you have a way to get the component price
                    quantity=pc_component.quantity
                )

                # Update stock levels
                pc_component.component.stockLevel -= pc_component.quantity
                pc_component.component.save()

            logger.info(f"Successfully created CustomPCOrder {custom_pc_order.id}")

            # Remove the build from CustomPC
            custom_pc.delete()

            return JsonResponse({
                'success': True,
                'order_id': custom_pc_order.id
            })
        except CustomPC.DoesNotExist:
            logger.error(f"CustomPC with id {build_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Custom PC build not found',
                'order_placed': False
            })
        except Address.DoesNotExist:
            logger.error(f"Address with id {address_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Address not found',
                'order_placed': False
            })
        except Exception as e:
            logger.error(f"Error in payment_success_custom_pc: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'order_placed': False
            })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method',
        'order_placed': False
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import CustomPCOrder, CustomPCComponent, Address, CustomPC, Component
import json
import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))

@csrf_exempt
@require_POST
def check_stock_availability(request):
    data = json.loads(request.body)
    custom_pc_id = data.get('custom_pc_id')

    if not custom_pc_id:
        return JsonResponse({'success': False, 'message': 'No custom PC selected.'})

    try:
        custom_pc = get_object_or_404(CustomPC, id=custom_pc_id, user=request.user)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid custom PC ID.'})

    all_in_stock = True
    out_of_stock_items = []

    for custom_component in custom_pc.components.all():
        component = custom_component.component
        if custom_component.quantity > component.stockLevel:
            all_in_stock = False
            out_of_stock_items.append(component.name)

    if all_in_stock:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'success': False,
            'message': f"The following items are out of stock: {', '.join(out_of_stock_items)}"
        })

@csrf_exempt
@require_POST
def place_custom_order(request):
    data = json.loads(request.body)
    address_id = data.get('address_id')
    payment_method = data.get('payment_method')
    custom_pc_id = data.get('custom_pc_id')
    user = request.user

    address = get_object_or_404(Address, id=address_id, user=user)
    custom_pc = get_object_or_404(CustomPC, id=custom_pc_id, user=user)
    total_amount = custom_pc.total_price

    if payment_method == 'razorpay':
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_amount * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create CustomPCOrder
        order = CustomPCOrder.objects.create(
            build=custom_pc,
            user=user,
            address=address,
            total_price=total_amount,
            razorpay_order_id=razorpay_order['id'],
            status='pending'
        )

        # Create OrderComponent entries
        for component in custom_pc.components.all():
            OrderComponent.objects.create(
                order=order,
                component_name=component.component.name,
                brand=component.component.brand,
                category=component.component.category,
                price=component.component.price,
                quantity=component.quantity
            )

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'total_amount': total_amount
        })
    elif payment_method == 'cod':
        # Create CustomPCOrder
        order = CustomPCOrder.objects.create(
            build=custom_pc,
            user=user,
            address=address,
            total_price=total_amount,
            status='pending'
        )

        # Create OrderComponent entries
        for component in custom_pc.components.all():
            OrderComponent.objects.create(
                order=order,
                component_name=component.component.name,
                brand=component.component.brand,
                category=component.component.category,
                price=component.component.price,
                quantity=component.quantity
            )

        return JsonResponse({'success': True, 'order_id': order.id})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid payment method'})

@csrf_exempt
@require_POST
def razorpay_callback(request):
    data = json.loads(request.body)
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    # Verify the payment signature
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except:
        return JsonResponse({'success': False, 'message': 'Invalid payment signature'})

    # Update the order status
    order = get_object_or_404(CustomPCOrder, razorpay_order_id=razorpay_order_id)
    order.status = 'paid'
    order.payment_id = razorpay_payment_id
    order.save()

    # Update stock levels
    for order_component in order.components.all():
        component = Component.objects.get(name=order_component.component_name)
        component.stockLevel -= order_component.quantity
        component.save()

    return JsonResponse({'success': True, 'message': 'Payment successful'})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from django.db.models import Prefetch

@login_required
def order_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        orders = Order.objects.filter(user_id=user_id).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        ).order_by('-created_at')
        context = {
            'orders': orders,
        }
        return render(request, 'order.html', context)
    else:
        return redirect('userapp:login')
    
@login_required
def build_order_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        build_orders = CustomPCOrder.objects.filter(user_id=user_id).exclude(
            status__in=['pending', 'rejected']
        ).prefetch_related('components').select_related('build', 'address').order_by('-created_at')
        
        context = {
            'build_orders': build_orders,
        }
        return render(request, 'build_order.html', context)
    else:
        return redirect('userapp:login')
    
    
from django.shortcuts import render
from .models import CustomPCOrder, OrderComponent
def ordered_build(request):
    # Get orders with their related deliveries and delivery boys
    orders = CustomPCOrder.objects.all().prefetch_related(
        'deliveries',
        'components'
    ).select_related('user')
    
    # Get all delivery boys except the currently assigned one
    delivery_boys = DeliveryBoy.objects.select_related('user').exclude(
        id__in=Delivery.objects.filter(
            status='assigned',
            orderId__in=orders.values_list('id', flat=True)
        ).values('deliveryBoyId')
    )
    
    context = {
        'orders': orders,
        'delivery_boys': delivery_boys
    }
    return render(request, 'ordered_build.html', context)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CustomPCOrder

# ... existing views ...

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CustomPCOrder

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def update_order_status(request, order_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        logger.info(f"Attempting to update order {order_id} to status {new_status}")
        
        order = CustomPCOrder.objects.get(id=order_id)
        old_status = order.status
        order.status = new_status
        order.save()
        
        logger.info(f"Order {order_id} updated: {old_status} -> {new_status}")
        
        return JsonResponse({
            'success': True,
            'status': order.get_status_display()
        })
    except CustomPCOrder.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return JsonResponse({
            'success': False,
            'error': 'Order not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
        
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.conf import settings
from .models import CustomPCOrder

logger = logging.getLogger(__name__)

def send_cancellation_email(user, order):
    subject = 'Order Cancellation Confirmation'
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"""
    Dear {user.username},

    Your order (ID: {order.id}) has been successfully cancelled. 
    The refund of ${order.total_price:.2f} will be processed within 3 working days.

    Order Details:
    - Order ID: {order.id}
    - Total Amount: ${order.total_price:.2f}
    - Cancelled Date: {current_time}

    If you have any questions about your refund, please contact our customer support.

    Thank you for your understanding.

    Best regards,
    TechCraft Team
    """
    
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    
    try:
        email.send(fail_silently=False)
        logger.info(f"Cancellation email sent successfully to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send cancellation email to {user.email}. Error: {str(e)}")
        return False

@require_POST
def cancel_custom_order(request, order_id):
    logger.info(f"Attempting to cancel order {order_id} for user {request.user.username}")
    try:
        order = CustomPCOrder.objects.get(id=order_id, user=request.user)
        logger.info(f"Order {order_id} found. Current status: {order.status}")
        if order.status in ['paid', 'building', 'shipped', 'enroute']:
            order.status = 'pending'
            order.save()
            logger.info(f"Order {order_id} status updated to pending")

            email_sent = send_cancellation_email(request.user, order)
            logger.info(f"Email sent status for order {order_id}: {email_sent}")

            message = 'Order cancelled successfully. The refund will be processed within 3 working days.'
            if email_sent:
                message += ' An email confirmation has been sent.'
            else:
                message += ' However, there was an issue sending the confirmation email.'

            return JsonResponse({
                'success': True, 
                'message': message
            })
        else:
            logger.warning(f"Order {order_id} cannot be cancelled. Current status: {order.status}")
            return JsonResponse({'success': False, 'error': 'Order cannot be cancelled at this stage.'})
    except CustomPCOrder.DoesNotExist:
        logger.error(f"Order {order_id} not found for user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'Order not found.'})
    except Exception as e:
        logger.exception(f"Error cancelling order {order_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'})
    
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import io

@csrf_exempt
def predict_component(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Load a more suitable pre-trained model
        model_name = "google/vit-base-patch16-224"
        feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        model = AutoModelForImageClassification.from_pretrained(model_name)

        # Process the uploaded image
        image_file = request.FILES['image']
        image = Image.open(io.BytesIO(image_file.read())).convert('RGB')
        inputs = feature_extractor(images=image, return_tensors="pt")

        # Make a prediction
        with torch.no_grad():
            outputs = model(**inputs)

        # Get the predicted class and confidence
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get top 5 predictions
        top5_prob, top5_catid = torch.topk(probs, 5)
        
        # Mapping of general objects to computer components
        component_mapping = {
            "mouse": "Computer Mouse",
            "computer keyboard": "Keyboard",
            "monitor": "Monitor",
            "desktop computer": "CPU",
            "laptop": "Laptop",
            "hard disc": "Hard Drive",
            "printer": "Printer",
            "joystick": "Joystick",
            "microphone": "Microphone",
            "web site": "Graphics Card",
            "hand-held computer": "Tablet",
            "ipod": "Portable Device",
            "modem": "Network Device",
            "electric fan": "Cooling Fan",
            "digital clock": "Digital Component"
        }

        top5_predictions = []
        for i in range(5):
            pred_class = model.config.id2label[top5_catid[0][i].item()]
            confidence = top5_prob[0][i].item() * 100
            mapped_component = component_mapping.get(pred_class.lower(), "Unknown Component")
            top5_predictions.append({
                "class": pred_class,  # Use the original class as the main prediction
                "mapped_class": mapped_component,
                "confidence": confidence
            })

        return JsonResponse({
            'predicted_class': top5_predictions[0]['class'],
            'mapped_class': top5_predictions[0]['mapped_class'],
            'confidence': top5_predictions[0]['confidence'],
            'top_5_predictions': top5_predictions
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

def ml_implement(request):
    return render(request, 'ml.html')

@login_required
def delivery_dashboard(request):
    if request.user.role != 'delivery_boy':
        return redirect('userapp:mainpage')
    return render(request, 'delivery_dashboard.html')

@login_required
def delivery_profile(request):
    # Get or create delivery profile
    delivery_profile, created = DeliveryBoy.objects.get_or_create(
        user=request.user,
        defaults={
            'joined_date': timezone.now()  # Use joined_date instead of date_joined
        }
    )
    
    context = {
        'user': request.user,
        'delivery_profile': delivery_profile
    }
    return render(request, 'delivery_profile.html', context)

@login_required
def update_delivery_profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Update user information
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.mobile = request.POST.get('mobile')
        user.save()

        # Check if delivery profile exists
        try:
            delivery_profile = DeliveryBoy.objects.get(user=user)
            # Update fields for existing profile
            delivery_profile.vehicle_number = request.POST.get('vehicle_number', '')
            delivery_profile.address = request.POST.get('address', '')
            delivery_profile.district = request.POST.get('district', '')
            delivery_profile.pincode = request.POST.get('pincode', '')
            delivery_profile.save(update_fields=['vehicle_number', 'address', 'district', 'pincode'])
        except DeliveryBoy.DoesNotExist:
            # Create new profile with current timestamp
            delivery_profile = DeliveryBoy.objects.create(
                user=user,
                vehicle_number=request.POST.get('vehicle_number', ''),
                address=request.POST.get('address', ''),
                district=request.POST.get('district', ''),
                pincode=request.POST.get('pincode', ''),
                joined_date=timezone.now()
            )

        messages.success(request, 'Profile updated successfully!')
        return redirect('userapp:delivery_profile')

    delivery_profile = getattr(request.user, 'delivery_profile', None)
    return render(request, 'update_delivery_profile.html', {
        'user': request.user,
        'delivery_profile': delivery_profile
    })
@login_required
def delivery_assigned(request):
    # Get the logged-in delivery boy
    delivery_boy = DeliveryBoy.objects.get(user=request.user)
    
    # Get all deliveries for this delivery boy with status 'assigned' or 'acceptedassigned' or 'onway'
    assigned_deliveries = Delivery.objects.filter(
        deliveryBoyId=delivery_boy,
        status__in=['assigned', 'acceptedassigned', 'onway']
    ).order_by('-assignedDate')
    
    print("Found deliveries:", assigned_deliveries)  # Debug print
    for delivery in assigned_deliveries:
        print(f"Delivery {delivery.deliveryId}: Status = {delivery.status}")  # Debug print
    
    context = {
        'assigned_deliveries': assigned_deliveries,
        'delivery_boy': delivery_boy
    }
    
    return render(request, 'delivery_assigned.html', context)

@login_required
def delivery_completed(request):    
    return render(request, 'delivery_completed.html')

@login_required
def delivery_cancelled(request):
    return render(request, 'delivery_cancelled.html')   

from django.http import JsonResponse
from django.utils import timezone
import json
from .models import Delivery, CustomPCOrder, DeliveryBoy
import traceback  # Add this import

def assign_delivery_boy(request, order_id):
    if request.method == 'POST':
        try:
            # Print request data for debugging
            print("Request received for order_id:", order_id)
            print("Request body:", request.body)
            
            data = json.loads(request.body)
            delivery_boy_id = data.get('delivery_boy_id')
            print("Delivery boy ID:", delivery_boy_id)
            
            # Get the order and delivery boy objects
            order = CustomPCOrder.objects.get(id=order_id)
            print("Order found:", order.id)
            
            delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)
            print("Delivery boy found:", delivery_boy.id)

            # Check if delivery already exists
            existing_delivery = Delivery.objects.filter(orderId=order).first()
            if existing_delivery:
                print("Existing delivery found, updating...")
                existing_delivery.delete()

            # Create new Delivery record
            delivery = Delivery.objects.create(
                orderId=order,
                deliveryBoyId=delivery_boy,
                status='assigned',
                assignedDate=timezone.now()
            )
            print("New delivery created:", delivery.deliveryId)
            
            # Update delivery boy status
            delivery_boy.status = 'assigned'
            delivery_boy.save()
            print("Delivery boy status updated")

            return JsonResponse({
                'success': True,
                'message': 'Delivery boy assigned successfully',
                'delivery_id': delivery.deliveryId
            })

        except CustomPCOrder.DoesNotExist:
            error_msg = f"Order not found: {order_id}"
            print(error_msg)
            return JsonResponse({'success': False, 'error': error_msg})
            
        except DeliveryBoy.DoesNotExist:
            error_msg = f"Delivery boy not found: {delivery_boy_id}"
            print(error_msg)
            return JsonResponse({'success': False, 'error': error_msg})
            
        except Exception as e:
            error_msg = f"Error in assign_delivery_boy: {str(e)}"
            print(error_msg)
            print("Full traceback:")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': error_msg})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Delivery, CustomPCOrder  # Make sure to import the models
import json
from django.views.decorators.csrf import ensure_csrf_cookie
import logging

logger = logging.getLogger(__name__)

@login_required
@require_POST
@ensure_csrf_cookie
def update_delivery_status(request, delivery_id):
    try:
        print(f"Received request for delivery_id: {delivery_id}")
        
        if not request.body:
            return JsonResponse({
                'success': False,
                'error': 'Empty request body'
            }, status=400)
            
        data = json.loads(request.body)
        status = data.get('status')
        
        if not status:
            return JsonResponse({
                'success': False,
                'error': 'Status is required'
            }, status=400)
            
        print(f"Processing status update: {status}")
        
        try:
            delivery = Delivery.objects.get(deliveryId=delivery_id)
            print(f"Found delivery: {delivery.deliveryId}")
            
        except Delivery.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Delivery with id {delivery_id} not found'
            }, status=404)
        
        if status == 'acceptedassigned':
            print("Processing accept request")
            # Update delivery status
            delivery.status = 'acceptedassigned'
            delivery.save()
            print(f"Updated delivery status to: {delivery.status}")
            
            # Update order status to enroute
            order = delivery.orderId
            order.status = 'enroute'  # Change order status to enroute
            order.save()
            print(f"Updated order status to: {order.status}")
            
            # Update delivery boy status
            delivery_boy = delivery.deliveryBoyId
            delivery_boy.status = 'assigned'  # Update delivery boy status
            delivery_boy.save()
            print(f"Updated delivery boy status to: {delivery_boy.status}")
            
            return JsonResponse({
                'success': True,
                'message': 'Delivery assignment accepted successfully'
            })
            
        elif status == 'declined':
            delivery.status = 'declined'
            delivery.save()
            
            # Update order status
            order = delivery.orderId
            order.status = 'shipped'
            order.save()
            
            # Update delivery boy status
            delivery_boy = delivery.deliveryBoyId
            delivery_boy.status = 'available'
            delivery_boy.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Delivery assignment declined successfully'
            })
            
        elif status == 'onway':
            delivery.status = 'onway'
            delivery.save()
            return JsonResponse({
                'success': True,
                'message': 'Delivery status updated to On The Way'
            })
            
        elif status == 'delivered':
            delivery.status = 'delivered'
            delivery.deliveryDate = timezone.now()
            delivery.save()
            
            # Update delivery boy status
            delivery_boy = delivery.deliveryBoyId
            delivery_boy.status = 'available'
            delivery_boy.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Delivery completed successfully'
            })
            
        else:
            return JsonResponse({
                'success': False,
                'error': f'Invalid status: {status}'
            }, status=400)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def update_delivery_status(request, delivery_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            update_order = data.get('update_order', False)
            
            delivery = Delivery.objects.get(deliveryId=delivery_id)
            delivery.status = new_status
            delivery.save()

            # If delivery is marked as delivered, update the order status
            if update_order and new_status == 'delivered':
                order = delivery.orderId
                order.status = 'arrived'  # Update this to match your order status field
                order.save()

            return JsonResponse({
                'success': True,
                'message': 'Status updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@login_required
def send_delivery_otp(request, delivery_id):
    if request.method == 'POST':
        try:
            delivery = Delivery.objects.get(deliveryId=delivery_id)
            order = delivery.orderId
            user_email = order.user.email
            
            # Generate OTP
            otp = generate_otp()
            
            # Store OTP in session
            request.session[f'delivery_otp_{delivery_id}'] = otp
            
            # Send email
            subject = 'Delivery Verification OTP'
            message = f'Your delivery verification OTP is: {otp}\nPlease provide this OTP to the delivery person to confirm your delivery.'
            from_email = 'your-email@example.com'  # Update with your email
            recipient_list = [user_email]
            
            send_mail(subject, message, from_email, recipient_list)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def verify_delivery_otp(request, delivery_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            submitted_otp = data.get('otp')
            stored_otp = request.session.get(f'delivery_otp_{delivery_id}')
            
            if submitted_otp == stored_otp:
                # Clear OTP from session after successful verification
                del request.session[f'delivery_otp_{delivery_id}']
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid OTP'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def chatbot_view(request):
    return render(request, 'chatbot.html')

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required
def get_cart_total(request):
    
    if request.method == 'GET':
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Please log in to view your cart'
                })

            with connection.cursor() as cursor:
                # Updated query to use correct table names based on your models
                cursor.execute("""
                    SELECT 
                        p.name as product_name,
                        c.quantity,
                        p.price,
                        (p.price * c.quantity) as subtotal,
                        p.productId as product_id
                    FROM userapp_cart c
                    JOIN userapp_product p ON c.product_id = p.productId
                    WHERE c.user_id = %s
                """, [user_id])
                
                cart_items = []
                total = 0
                
                for row in cursor.fetchall():
                    item = {
                        'name': row[0],
                        'quantity': row[1],
                        'price': float(row[2]),
                        'subtotal': float(row[3]),
                        'product_id': row[4]
                    }
                    cart_items.append(item)
                    total += item['subtotal']

                return JsonResponse({
                    'success': True,
                    'cart_items': cart_items,
                    'total': total,
                    'item_count': len(cart_items)
                })

        except Exception as e:
            print(f"Error fetching cart data: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error retrieving cart information'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })
