from django.shortcuts import render

# Create your views here.

from multiprocessing import context
from django.shortcuts import redirect, render
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import never_cache

from django.db.models import Q

from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from accounts.models import Account
from adminpanel.forms import CategoryForm,ProductForm, VariationForm
from store.models import Product, Variation
from orders.models import Order, OrderProduct, Coupon
from category.models import Category

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa



def redirect_to_login(request):
  return redirect('manager_login')

@never_cache
def manager_login(request):
  if request.user.is_authenticated:
    if request.user.is_admin:
      return redirect('manager_dashboard')
    else:
      return redirect('home')
  else:
    if request.method == 'POST':
      email = request.POST['email']
      password = request.POST['password']
      
      user = authenticate(request, username=email, password=password)
      if user is not None:
        if user.is_admin:
            login(request, user)
            return redirect('manager_dashboard')
        else:
            messages.warning(request, 'You are logged in a non-staff account')
      else:
        messages.error(request, 'Email or Password is incorrect')
  return render(request, 'manager/manager_signin.html')

@never_cache
def manager_logout(request):
  logout(request)
  return redirect('manager_login')

# dashboard
@never_cache
@login_required(login_url='manager_login')
def manager_dashboard(request):
  if request.user.is_admin:
    
    user_count = Account.objects.filter(is_admin=False).count()
    product_count = Product.objects.all().count()
    product = Product.objects.all()
    order_count = Order.objects.filter(is_ordered=True).count()
    category_count = Category.objects.all().count()
    
    total_sales = 0
    orders = Order.objects.filter(is_ordered=True)
    for order in orders:
      total_sales += order.order_total
    
    context = {
      'user_count': user_count,
      'product_count': product_count,
      'product': product,
      'order_count': order_count,
      'category_count': category_count,
      'total_sales': int(total_sales)
    }
    
    return render(request, 'manager/manager_dashboard.html', context)
  else:
    return redirect('home')

# User Management
@never_cache
@login_required(login_url='manager_login')
def manage_user(request):
  if request.user.is_admin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      users = Account.objects.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(username__icontains=keyword) | Q(email__icontains=keyword) | Q(phone_number__icontains=keyword)).order_by('id')
    
    else:
      users = Account.objects.filter(is_admin=False).order_by('id')
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)
    
    context = {
      'users': paged_users,
    }
    return render(request, 'manager/user_management.html', context) 
  
  else:
    return redirect('home')

# Ban User
@never_cache
@login_required(login_url='manager_login')
def ban_user(request, user_id):
  if request.user.is_admin:
    user = Account.objects.get(id=user_id)
    user.is_active = False
    user.save()

    return redirect('manage_user')
  
  else:
    return redirect('home')

# UnBan User
@never_cache
@login_required(login_url='manager_login')
def unban_user(request, user_id):
  if request.user.is_admin:
    user = Account.objects.get(id=user_id)
    user.is_active = True
    user.save()

    return redirect('manage_user')
  
  else:
    return redirect('home')


# Manage Category
@never_cache
@login_required(login_url='manager_login')
def manage_category(request):
  if request.user.is_admin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      categories = Category.objects.filter(Q(category_name__icontains=keyword) | Q(slug__icontains=keyword)).order_by('id')
      
    else:
      categories = Category.objects.all().order_by('id')
    
    paginator = Paginator(categories, 10)
    page = request.GET.get('page')
    paged_categories = paginator.get_page(page) 
    
    context = { 
      'categories': paged_categories
    } 
    
    return render(request, 'manager/category_management.html', context)  
  
  else:
    return redirect('home')


# Add category
@never_cache
@login_required(login_url='manager_login')
def add_category(request):
  if request.user.is_admin:
    form = CategoryForm()
    if request.method == 'POST':
      try:
        form = CategoryForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
          form.save()
        return redirect('manage_category')
      
      except Exception as e:
        raise e
    
    return render(request, 'manager/category_add.html', {'form': form})
  
  else:
    return redirect('home')


# Delete Category
@never_cache
@login_required(login_url='manager_login')
def delete_category(request, category_id):
  if request.user.is_admin:
    category = Category.objects.get(id=category_id)
    category.delete()
    
    return redirect('manage_category')
  
  else:
    return redirect('home')


# Product Management
@never_cache
@login_required(login_url='manager_login')
def manage_product(request):
  if request.user.is_admin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      products = Product.objects.filter(Q(product_name__icontains=keyword) | Q(slug__icontains=keyword) | Q(category__category_name__icontains=keyword)).order_by('id')
    
    else:
      products = Product.objects.all().order_by('id')
    
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    
    context = {
      'products': paged_products
    }
    return render(request, 'manager/product_management.html', context)
  
  else:
    return redirect('home')


# Delete Product
@never_cache
@login_required(login_url='manager_login')
def delete_product(request, product_id):
  if request.user.is_admin:
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('manage_product')
  
  else:
    return redirect('home')


# Add Product
@never_cache
@login_required(login_url='manager_login')
def add_product(request):
  if request.user.is_admin:
    if request.method == 'POST':
      form = ProductForm(request.POST, request.FILES)
      if form.is_valid():
          form.save()
          return redirect('manage_product')
    else:
      form = ProductForm()
      context = {
        'form': form
      }
      return render(request, 'manager/add_product.html', context)

  else:
    return redirect('home')

# Edit Product
@never_cache
@login_required(login_url='manager_login')
def edit_product(request, product_id):
  if request.user.is_admin:
    product = Product.objects.get(id=product_id)
    form = ProductForm(instance=product)
    
    if request.method == 'POST':
      try:
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
          form.save()
          
          return redirect('manage_product')
      
      except Exception as e:
        raise e

    context = {
      'product': product,
      'form': form
    }
    return render(request, 'manager/edit_product.html', context)
  
  else:
    return redirect('home')


# Manage Variation
@never_cache
@login_required(login_url='manager_login')
def manage_variation(request):
  if request.user.is_admin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      variations = Variation.objects.filter(Q(product__product_name__icontains=keyword) | Q(variation_category__icontains=keyword) | Q(variation_value__icontains=keyword)).order_by('id')
    
    else:
      variations = Variation.objects.all().order_by('id')
    
    paginator = Paginator(variations, 10)
    page = request.GET.get('page')
    paged_variations = paginator.get_page(page)
    
    context = {
      'variations': paged_variations
    }
    return render(request, 'manager/variation_management.html', context)

  else:
    return redirect('home')


@never_cache
@login_required(login_url='manager_login')
def delete_variation(request, variation_id):
  if request.user.is_admin:
    variation = Variation.objects.get(id=variation_id)
    variation.delete()
    return redirect('manage_variation')

  else:
    return redirect('home')

# Add Variation
@never_cache
@login_required(login_url='manager_login')
def add_variation(request):
  if request.user.is_admin:
    if request.method == 'POST':
      form = VariationForm(request.POST)
      if form.is_valid():
        form.save()
        return redirect('manage_variation')
    
    else:
      form = VariationForm()
    
    context = {
      'form': form
    }
    return render(request, 'manager/add_variation.html', context)
  
  else:
    return redirect('home')
  

# Update Variation
@never_cache
@login_required(login_url='manager_login')
def update_variation(request, variation_id):
  if request.user.is_admin:
    variation = Variation.objects.get(id=variation_id)
  
    if request.method == 'POST':
      form = VariationForm(request.POST ,instance=variation)
      if form.is_valid():
        form.save()
        return redirect('manage_variation')
    
    else:
      form = VariationForm(instance=variation)
    
    context = {
      'variation': variation,
      'form': form
    }
    return render(request, 'manager/update_variation.html', context)
  
  else:
    return redirect('home')



# My orders
@login_required(login_url='manager_login')
def admin_order(request):
  if request.user.is_admin:
    current_user = request.user
  
    if request.method == 'POST':
      keyword = request.POST['keyword']
      orders = Order.objects.filter(Q(user=current_user), Q(is_ordered=True), Q(order_number__icontains=keyword) | Q(user__email__icontains=keyword) | Q(firstname__icontains=keyword) | Q(lastname__icontains=keyword) | Q(phone_number__icontains=keyword)).order_by('-created_at')
      
    else:
      orders = Order.objects.filter(user=current_user, is_ordered=True).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
      'orders': paged_orders,
    }
    return render(request, 'manager/admin_orders.html', context)
  
  else:
    return redirect('home')

# Manage Order
@never_cache
@login_required(login_url='manager_login')
def manage_order(request):
  if request.user.is_admin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      orders = Order.objects.filter(Q(is_ordered=True), Q(order_number__icontains=keyword) | Q(user__email__icontains=keyword) | Q(firstname__icontains=keyword) | Q(lastname__icontains=keyword)).order_by('-order_number')
    
    else:
      orders = Order.objects.filter(is_ordered=True).order_by('order_number')
      
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
      'orders': paged_orders
    }
    return render(request, 'manager/order_management.html', context)
  
  else:
    return redirect('home')


# Cancel Order
@never_cache
@login_required(login_url='manager_login')
def cancel_order(request, order_number):
  if request.user.is_admin:
    order = Order.objects.get(order_number=order_number)
    order.status = 'Cancelled'
    order.save()
    
    return redirect('manage_order')
  
  else:
    return redirect('home')
    

# Accept Order
@never_cache
@login_required(login_url='manager_login')
def accept_order(request, order_number):
  if request.user.is_admin:
    order = Order.objects.get(order_number=order_number)
    order.status = 'Accepted'
    order.save()
    
    return redirect('manage_order')
  
  else:
    return redirect('home')

# Complete Order
@never_cache
@login_required(login_url='manager_login')
def complete_order(request, order_number):
  if request.user.is_admin:
    order = Order.objects.get(order_number=order_number)
    order.status = 'Completed'
    order.save()
    
    return redirect('manage_order')
  
  else:
    return redirect('home')



#COUPON MANAGEMENT
@login_required(login_url='signin')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def coupon_management(request):
    if request.method == 'POST':
        key = request.POST['key']
        coupon = Coupon.objects.filter(Q(coupon_code__icontains=key))
    else:
        coupon = Coupon.objects.all()

    context = {
        'coupons': coupon
    }

    return render(request, 'manager/coupon_management.html', context)


def update_coupon(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)

        if request.method == 'POST':
            coupon_code = request.POST['coupon_code'] 
            minimum_amount = request.POST['minimum_amount'] 
            discount_price = request.POST['discount_price'] 
            expiry_at = request.POST['expiry_at'] 

            coupon.coupon_code = coupon_code
            coupon.minimum_amount = minimum_amount
            coupon.discount_price = discount_price
            coupon.expiry_at = expiry_at

            coupon.save()
            return redirect('coupon_management')

        context = {
            'coupon': coupon
        }
    except Exception as e:
        raise e
    
    return render(request, 'manager/update_coupon.html', context)



def delete_coupon(request, coupon_id):
    coupon = Coupon.objects.filter(id=coupon_id)
    coupon.delete()
    return redirect('coupon_management')


def add_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST['coupon_code'] 
        minimum_amount = request.POST['minimum_amount'] 
        discount_price = request.POST['discount_price'] 
        expiry_at = request.POST['expiry_at']

        coupon = Coupon(
            coupon_code=coupon_code,
            minimum_amount=minimum_amount,
            discount_price=discount_price,
            expiry_at=expiry_at
        )

        coupon.save()
        return redirect('coupon_management')
    return render(request, 'manager/add_coupon.html')

#sales report
# Manage Order
@never_cache
@login_required(login_url='manager_login')
def manage_sales(request):
  if request.user.is_admin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      orders = Order.objects.filter(Q(is_ordered=True), Q(order_number__icontains=keyword) | Q(user__email__icontains=keyword) | Q(firstname__icontains=keyword) | Q(lastname__icontains=keyword)).order_by('-order_number')
    
    else:
      orders = Order.objects.filter(is_ordered=True).order_by('order_number')
      
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
      'orders': paged_orders
    }
    return render(request, 'manager/sales_management.html', context)
  
  else:
    return redirect('home')

def pdf_report_create(request):
    orders = OrderProduct.objects.all()
    orders = Order.objects.filter(is_ordered=True).order_by('-order_number')

    template_path = 'manager/pdf.html'

    context = {'orders': orders}

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="products_report.pdf"'

    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def csv_report_create(request):
    orders = OrderProduct.objects.all()
    orders = Order.objects.filter(is_ordered=True).order_by('-order_number')

    template_path = 'manager/csv.html'

    context = {'orders': orders}

    response = HttpResponse(content_type='application/csv')

    response['Content-Disposition'] = 'attachment; filename="products_report.csv"'

    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response