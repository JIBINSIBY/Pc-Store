from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login,get_user_model,logout
from django.contrib import messages
# from .models import*
import re
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from .forms import UserUpdateForm
from .models import Address, Product, Component, ProductImage, Cart, Rating, CustomPC, CustomPCComponent
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

    context = {
        'latest_monitors': latest_monitors,
        'latest_keyboards': latest_keyboards,
        'latest_assembledcpu': latest_assembledcpu,
        'latest_mice': latest_mice,
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
                return redirect(reverse('userapp:loginuser'))
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
            elif u.role == 'staff':
                redirect_url = reverse('userapp:staff_dashboard')
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



@require_POST
def delete_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'success': True})

@require_POST
def change_user_role(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    data = json.loads(request.body)
    new_role = data.get('role')
    
    if new_role in ['user', 'staff']:
        user.role = new_role
        user.is_staff = (new_role == 'staff')
        user.is_superuser = False
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid role'})

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
def admin_viewcomponent(request):
    components = Component.objects.all()
    return render(request, 'admin_viewcomponent.html', {'components': components})

@login_required(login_url='userapp:login')
def admin_editcomponent(request, component_id):
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

@require_POST
def delete_component(request, component_id):
    try:
        component = Component.objects.get(componentId=component_id)
        component.delete()
        return JsonResponse({'success': True})
    except Component.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Component not found'}, status=404)
    except Exception as e:
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
    return render(request, 'pc_custom.html')


@login_required(login_url='userapp:login')
def keyboards_view(request):
    keyboards = Product.objects.filter(category='keyboard')
    available_brands = keyboards.values_list('brand', flat=True).distinct()
    context = {
        'keyboards': keyboards,
        'available_brands': available_brands,
    }
    return render(request, 'keyboards.html', context)

@login_required(login_url='userapp:login')
def mouses_view(request):
    mouses = Product.objects.filter(category='mouse')
    available_brands = mouses.values_list('brand', flat=True).distinct()
    context = {
        'mouses': mouses,
        'available_brands': available_brands,
    }
    return render(request, 'mouse.html', context)

@login_required(login_url='userapp:login')
def monitors_view(request):
    monitors = Product.objects.filter(category='monitor')
    available_brands = monitors.values_list('brand', flat=True).distinct()
    context = {
        'monitors': monitors,
        'available_brands': available_brands,
    }
    return render(request, 'monitors.html', context)

@login_required(login_url='userapp:login')
def assembledcpus_view(request):
    assembledcpus = Product.objects.filter(category='assembled_cpu')
    available_brands = assembledcpus.values_list('brand', flat=True).distinct()
    context = {
        'assembledcpus': assembledcpus,
        'available_brands': available_brands,
    }
    return render(request, 'assembled_cpu.html', context)

@login_required(login_url='userapp:login')
def accessories_view(request):
    accessories = Product.objects.filter(category='accessory')
    available_brands = accessories.values_list('brand', flat=True).distinct()
    context = {
        'accessories': accessories,
        'available_brands': available_brands,
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

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'delivery_charges': delivery_charges,
        'total_amount': total_amount,
        'total_savings': total_savings,
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

@login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    user_addresses = Address.objects.filter(user=user)
    total_price = sum(item.totalPrice for item in cart_items)
    total_discount = 0  # Calculate this based on your discount logic
    delivery_charges = 174  # You can adjust this or make it dynamic
    total_amount = total_price - total_discount + delivery_charges
    total_savings = total_discount
    
    context = {
        'user': user,
        'cart_items': cart_items,
        'user_addresses': user_addresses,
        'total_price': total_price,
        'total_discount': total_discount,
        'delivery_charges': delivery_charges,
        'total_amount': total_amount,
        'total_savings': total_savings,
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

            # Create a new CustomPC instance
            custom_pc = CustomPC.objects.create(
                user=request.user,
                total_price=total_price,
                status='Pending'  # You can set an initial status
            )

            # Add components to CustomPCComponent
            for component_data in components:
                component = Component.objects.get(componentId=component_data['componentId'])
                CustomPCComponent.objects.create(
                    custom_pc=custom_pc,
                    component=component,
                    quantity=component_data['quantity']
                )

            return JsonResponse({'success': True, 'message': 'Configuration submitted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})