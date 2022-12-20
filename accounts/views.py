from django.shortcuts import render
from django.contrib import messages,auth
from django.shortcuts import render,redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator

from django.db.models import Q

from cart.views import _cart_id 
from cart.models import Cart,CartItem

# verification_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import requests

from . models import Account , UserProfile
from . forms import RegistrationForm, UserForm, UserProfileForm
from orders.models import Order, OrderProduct

# Create your views here.

def signup(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)   
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            username = email.split("@")[0]    # username is not created by user.so we are automatically creating it while user registration by spling email name.

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=username ) # 
            user.phone_number = phone_number                                                                                        
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)   #geting current site(default:localhost)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user' : user,                                        # to pass user object,like (user.name) in vrfction
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),  # encoding user id by using urlSafe method to keep it secure
                'token' : default_token_generator.make_token(user),   # default token - library, make_token creates token for users
            })                                # email body which we are sending for verification
            to_email = email
            send_email = EmailMessage(mail_subject, message, to = [to_email]) 
            send_email.send()  

            # messages.success(request,"Thank You for registering with us.We have sent you a verification mail to your email address.Please verify it.") -- This lasts only 4 seconds
            return redirect('/accounts/signin/?command=verification&email='+email)         

    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/signup.html', context) #If, if case doesn't get saved, it is rendered to signup page itself 

@never_cache
def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user=auth.authenticate(request,email=email,password=password)

        if user is not None:   # request.session
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    # getting product variation by cartid
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation)) #appending it as list, bcoz by default it is query set

                    # get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user=user) #right user -> authenticated user
                    ex_var_list = []  #all variations in cartitems list
                    id = []           #cart id
                    for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))     #it is a quer set, so we are converting to list using list() tag
                            id.append(item.id)
                    # getting products in product variation which are inside existing variation list 
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user) # name = user.name
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect('nextPage')
            except:
                return redirect('home')

        else:
            messages.error(request, "Incorrect username or password !")
            return redirect('signin')

    return render(request, 'accounts/signin.html')

@login_required(login_url = 'login')
def signout(request):
    auth.logout(request)
    messages.success(request,"Logged out Successfully")
    return redirect('home')


def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()         # decoding user id
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulations!your account is activated.')

        return redirect('signin')

    else:
        messages.error(request,'invalid activation link')
        return redirect('signup')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():     #checking if email exists or not
            user = Account.objects.get(email__iexact=email)

            # RESET PASSWORD EMAIL
            current_site=get_current_site(request)
            mail_subject="Reset your paassword"
            message= render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_mail = email
            send_email = EmailMessage(mail_subject, message, to=[to_mail])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('signin')
        else:
            messages.error(request, 'Account does  not exist!')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')

def resetPassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()         # decoding user id
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):  #chech token is used to chech whether it is secured token or not
        request.session['uid'] = uid   # To access the session later once password is reseted
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset is successfull')
            return redirect('signin')
            
        else:
            messages.error(request,'password do not match!')
            return redirect('resetPassword')
        
    else:
        return render(request,'accounts/resetPassword.html')

# Dashboard
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')

        # User Profile Generation
        user_profile = UserProfile.objects.create(
            user = user
        )
        user_profile.save()

        return redirect('signin')
    else:
        messages.error(request, "Invalid Activation Link")
        return redirect('signup')


@login_required(login_url ='signin')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    # check = UserProfile.objects.filter(user_id=request.user.id)
    # if len(check)>=0:

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count' : orders_count,
        'userprofile'  : userprofile,
    }
    return render(request, 'accounts/dashboard.html', context) 


def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    context = {
        'orders' : orders
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url ='signin')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile has been Updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }          
    return render(request, 'accounts/edit_profile.html', context )


# def edit_profile(request):
#     userprofile = get_object_or_404(UserProfile, user=request.user)
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=request.user)
#         profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, 'Your Profile has been Updated')
#             return redirect('edit_profile')
#     else:
#         user_form = UserForm(instance=request.user)
#         profile_form = UserProfileForm(instance=userprofile)
#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'userprofile': userprofile,
#     }            
    # return render(request, 'accounts/edit_profile.html', context )

def address(request):
    add = UserProfile.objects.filter(user = request.user)

    # add = Order.objects.filter(user = request.user)

    # order_detail = OrderProduct.objects.filter(order__order_number=order_id)  # order--> OrderProduct.order(foreignkey)   # __order_number --> Order.order_number (accessing via foreign key)
    # order = Order.objects.get(order_number=order_id)
    
    # order_number = request.session['order_number'] 
    # order = Order.objects.get(user=request.user, is_ordered=False)
    
    return render(request, 'accounts/address.html',{'add':add, 'active':'btn-primary'})


@login_required(login_url ='signin')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__iexact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password Updated Successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Current Password does not Match')
                return redirect('change_password')
            
        else:
            messages.error(request, 'Password Does not Match')
            return redirect('change_password')
                
    return render(request, 'accounts/change_password.html')


@login_required(login_url ='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)  # order--> OrderProduct.order(foreignkey)   # __order_number --> Order.order_number (accessing via foreign key)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        
    }
    return render(request, 'accounts/order_detail.html', context)



def user_manage_order(request):
      if request.user.is_admin:
            if request.method == 'POST':
                keyword = request.POST['keyword']
                orders = Order.objects.filter(Q(is_ordered=True), Q(order_number__icontains=keyword) | Q(user__email__icontains=keyword) | Q(firstname__icontains=keyword) | Q(lastname__icontains=keyword)).order_by('-order_number')
    
            else:
                orders = Order.objects.filter(is_ordered=True).order_by('-order_number')
      
            paginator = Paginator(orders, 10)
            page = request.GET.get('page')
            paged_orders = paginator.get_page(page)
            context = {
            'orders': paged_orders
            }
            return render(request, 'accounts/my_orders.html', context)
  
      else:
            return redirect('home')



@login_required(login_url='login')
def user_cancel_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Order Cancelled'
    order.save()
        
    return render(request, 'accounts/cancel_message.html')