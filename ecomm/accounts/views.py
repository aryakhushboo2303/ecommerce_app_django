from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
from .models import Profile
from products.models import *
from accounts.models import Cart, CartItems
import razorpay
from django.conf import settings



def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')

def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')



def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')

def add_to_cart(request, uid):
    print("uid:",uid)
    variant = request.GET.get('variant')
    product = Product.objects.get(uid=uid)
    print("product:",product)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)
    cart_item = CartItems.objects.create(cart = cart, product = product)
    if variant:
        variant = request.GET.get('variant')
        size_variant = SizeVariant.objects.get(size_name = variant)
        cart_item.size_variant = size_variant
        cart_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cart(request):
    cart_obj = Cart.objects.filter(is_paid=False, user=request.user)
    context = {'cart' : cart_obj }
    # cart_obj = Cart.objects.get(is_paid=False, user=request.user)
        # client = razorpay.Client(auth = (settings.KEY, settings.SECRET))
    # payment = client.order.create({
    # 'amount': cart_obj.get_cart_total() * 100,
    # 'currency': 'INR',
    # 'payment_capture': 1
    #  })
    # cart_obj.razor_pay_order_id  = payment['id']
    # context = { 'cart' : cart_obj, 'payment' : payment }
    return render(request, 'accounts/cart.html', context )

def remove_cart(request, uid):
    try:
        cart_item = CartItems.objects.get(uid = uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def success(request):
    order_id = request.GET.get('order_id')
    cart =  Cart.objects.get(razor_pay_order_id = order_id)
    cart.is_paid = True
    cart.save()
    return HttpResponse('Payment Success.........')