from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login,get_user_model,logout
from django.contrib import messages
# from .models import*
import re
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from .forms import UserUpdateForm
from .models import Address, Product, Component, ProductImage, Cart
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

user = get_user_model()
def index(request):
    latest_monitors = Product.objects.filter(Q(category='monitor')).order_by('-productId')[:3]
    print(f"Latest monitors: {latest_monitors}")
    latest_keyboards = Product.objects.filter(category='keyboard').order_by('-productId')[:3]
    print(f"Latest keyboards: {latest_keyboards}")
    latest_assembledcpu = Product.objects.filter(category='assembled_cpu').order_by('-productId')[:3]
    print(f"Latest assembled CPUs: {latest_assembledcpu}")
    context = {
        'latest_monitors': latest_monitors,
        'latest_keyboards': latest_keyboards,
        'latest_assembledcpu': latest_assembledcpu,
    }
    return render(request, 'index.html', context)

def mainpage(request):
    latest_monitors = Product.objects.filter(Q(category='monitor')).order_by('-productId')[:3]
    latest_keyboards = Product.objects.filter(category='keyboard').order_by('-productId')[:3]
    latest_assembledcpu = Product.objects.filter(category='assembled_cpu').order_by('-productId')[:3]
    latest_mice = Product.objects.filter(category='mouse').order_by('-productId')[:3]

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

def signout(request):
    logout(request)
    return redirect('userapp:login')

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


def admin_dashboard(request):
    return render(request, 'adminmain.html')


def admin_profile(request):
    return render(request, 'admin_profile.html', {'user': request.user})


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
    
    if new_role in ['user', 'staff', 'admin']:
        user.role = new_role
        user.is_staff = (new_role in ['staff', 'admin'])
        user.is_superuser = (new_role == 'admin')
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid role'})

def admin_productadd(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        stockLevel = request.POST.get('stockLevel')
        description = request.POST.get('description')
        main_image = request.FILES.get('main_image')
        additional_images = request.FILES.getlist('additional_images')

        product = Product(
            name=name,
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

def admin_viewcomponent(request):
    components = Component.objects.all()
    return render(request, 'admin_viewcomponent.html', {'components': components})

def admin_editcomponent(request, component_id):
    component = get_object_or_404(Component, componentId=component_id)
    if request.method == 'POST':
        component.name = request.POST.get('name')
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

def admin_addcomponent(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        stockLevel = request.POST.get('stockLevel')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        component = Component(
            name=name,
            category=category,
            price=price,
            stockLevel=stockLevel,
            description=description
        )

        if image:
            # Generate a unique filename
            file_name = f'{name}_{image.name}'
            file_path = os.path.join(settings.COMPONENT_IMAGES_DIR, file_name)
            os.makedirs(settings.COMPONENT_IMAGES_DIR, exist_ok=True)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            # Set the image field to the relative path
            component.image = os.path.join('component_images', file_name)

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

def pc_custom(request):
    return render(request, 'pc_custom.html')

from django.http import JsonResponse
from .models import Component

def get_components(request):
    components = Component.objects.all().values('componentId', 'name', 'category', 'price', 'image')
    component_list = list(components)
    for component in component_list:
        category = component['category'].lower().replace(' ', '')
        if category == 'cpu/processor':
            component['category'] = 'cpu'
        elif category == 'powersupplyunit':
            component['category'] = 'psu'
        elif category == 'graphicscard':
            component['category'] = 'gpu'
        elif category == 'bluetoothcard':
            component['category'] = 'bluetooth'
        elif category == 'wificard':
            component['category'] = 'wifi'
        else:
            component['category'] = category

        if component.get('image'):
            component['image'] = settings.MEDIA_URL + str(component['image'])
        else:
            component['image'] = settings.STATIC_URL + 'images/default-component.png'
    return JsonResponse(component_list, safe=False)

def keyboards_view(request):
    keyboards = Product.objects.filter(category='keyboard')
    print(f"Number of keyboards: {keyboards.count()}")
    for keyboard in keyboards:
        print(f"Keyboard ID: {keyboard.productId}")
    return render(request, 'keyboards.html', {'keyboards': keyboards})

def mouses_view(request):
    mouses = Product.objects.filter(category='mouse')
    return render(request, 'mouse.html', {'mouses': mouses})

def monitors_view(request):
    monitors = Product.objects.filter(category='monitor')
    return render(request, 'monitors.html', {'monitors': monitors})

def assembledcpus_view(request):
    assembledcpus = Product.objects.filter(category='assembled_cpu')
    return render(request, 'assembled_cpu.html', {'assembledcpus': assembledcpus})

def accessories_view(request):
    accessories = Product.objects.filter(category='accessory')
    return render(request, 'accessory.html', {'accessories': accessories})





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

def single_product(request, product_id):
    product = get_object_or_404(Product, productId=product_id)
    return render(request, 'singleproduct.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(productId=product_id)
    user = request.user
    
    # Check if the product is already in the cart
    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product,
        defaults={'quantity': 1, 'totalPrice': product.price}
    )
    
    if not created:
        # If the item already exists in the cart, increase the quantity
        cart_item.quantity += 1
        cart_item.totalPrice = cart_item.quantity * product.price
        cart_item.save()
    
    return redirect('userapp:cart_view')

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

@require_POST
@csrf_exempt
def update_cart_item(request, item_id):
    data = json.loads(request.body)
    new_quantity = data['quantity']
    cart_item = Cart.objects.get(cartId=item_id)
    product = cart_item.product

    if new_quantity > product.stockLevel:
        return JsonResponse({
            'success': False,
            'error': 'insufficient_stock',
            'available_stock': product.stockLevel
        })

    cart_item.quantity = new_quantity
    cart_item.totalPrice = cart_item.product.price * new_quantity
    cart_item.save()
    
    cart_total = sum(item.totalPrice for item in Cart.objects.filter(user=request.user))
    total_items = sum(item.quantity for item in Cart.objects.filter(user=request.user))
    
    return JsonResponse({
        'success': True,
        'new_price': cart_item.totalPrice,
        'cart_total': cart_total,
        'total_items': total_items
    })

@require_POST
@csrf_exempt
def remove_cart_item(request, item_id):
    Cart.objects.filter(cartId=item_id).delete()
    
    cart_items = Cart.objects.filter(user=request.user)
    cart_total = sum(item.totalPrice for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    total_discount = 0  # Calculate this based on your discount logic
    delivery_charges = 174  # You can adjust this or make it dynamic
    total_amount = cart_total - total_discount + delivery_charges
    
    return JsonResponse({
        'success': True,
        'cart_total': cart_total,
        'total_items': total_items,
        'total_discount': total_discount,
        'delivery_charges': delivery_charges,
        'total_amount': total_amount
    })

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
    image.delete()
    return JsonResponse({'success': True})