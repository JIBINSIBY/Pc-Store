from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login,get_user_model,logout
from django.contrib import messages
# from .models import*
import re
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from .forms import UserUpdateForm
from .models import Address, Product
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from django.conf import settings

user = get_user_model()
def index(request):
    return render(request,'index.html')
def mainpage(request):
    return render(request,'main.html')

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
    u=request.user
    if u.is_authenticated:
        return redirect('userapp:mainpage')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        u = authenticate(request, email=email, password=password)
        if u is not None:
            login(request, u)
            
            # Check user role and redirect accordingly
            if u.role == 'admin':
                return redirect(reverse('userapp:admin_dashboard'))
            elif u.role == 'staff':
                return redirect(reverse('userapp:staff_dashboard'))
            else:  # Assume 'user' role or any other role
                return redirect(reverse('userapp:mainpage'))
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'loginuser.html')
    return render(request, 'loginuser.html')

def forgotpassword(request):
    return render(request,'forgotpassword.html')

def profile(request):
    return render(request,'profile.html')

def profileedit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('userapp:profile')  # Redirect to a profile page or any other page
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request,'profileedit.html', {'form': form})

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
    return redirect(reverse('userapp:loginuser'))

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
    return render(request, 'admin_profile.html')


def update_admin_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('userapp:admin_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'update_admin_profile.html', {'form': form})

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
        image = request.FILES.get('image')

        product = Product(
            name=name,
            category=category,
            price=price,
            stockLevel=stockLevel,
            description=description
        )

        if image:
            # Generate a unique filename
            file_name = f'product_images/{name}_{image.name}'
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            # Set the image field to the relative path
            product.image = file_name

        product.save()
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
    if request.method == 'POST':
        # Handle form submission
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.stockLevel = request.POST.get('stockLevel')
        product.description = request.POST.get('description')
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('userapp:admin_viewproduct')
    
    return render(request, 'admin_editproduct.html', {'product': product})