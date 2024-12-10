from django.shortcuts import render, redirect
from .models import Product, Cart
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')
    
    return render(request, 'FreshShope_app/register.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'FreshShope_app/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def home(request):
    return render(request, 'FreshShope_app/home.html')

@never_cache
def view_products(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'FreshShope_app/view_products.html', {'page_obj': page_obj})

@never_cache
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"{product.name} added to cart!")
    return redirect('view_cart')

@never_cache
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)  # Get all cart items for the user
    total = 0  # Initialize total cart value

    # Calculate total price for each item and the overall total
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # Add a custom attribute for total price
        total += item.total_price

    return render(request, 'FreshShope_app/cart.html', {
        'cart_items': cart_items,
        'total': total,  # Pass the total cart price to the template
    })

@never_cache
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)  # Get items in the user's cart
    total = 0
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # Calculate total price for each item
        total += item.total_price  # Calculate the cart's total price

    return render(request, 'FreshShope_app/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })
  
@never_cache  
def remove_from_cart(request, item_id):
    try:
        cart_item = Cart.objects.get(id=item_id, user=request.user)
        cart_item.delete()  # Remove the item from the cart
    except Cart.DoesNotExist:
        pass  # Handle the case where the cart item does not exist
    return redirect('view_cart')  # Redirect back to the cart page

@never_cache
def increase_quantity(request, item_id):
    try:
        cart_item = Cart.objects.get(id=item_id, user=request.user)
        cart_item.quantity += 1
        cart_item.save()
    except Cart.DoesNotExist:
        pass
    return redirect('view_cart')
