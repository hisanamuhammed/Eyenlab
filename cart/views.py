from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product, Variation
from accounts.models import Account, UserProfile
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
        cart = request.session.session_key 
        if not cart:
                cart = request.session.create()
        return cart


def add_cart(request, product_id):
        current_user = request.user
        product = Product.objects.get(id=product_id) #get the product
#-------If user is authenticated-------- 
        if current_user.is_authenticated:
        # ---------VARIATION--------
                product_variation = []
                if request.method == 'POST':
                        for item in request.POST:
                                key = item 
                                value = request.POST[key]
                                try:
                                        variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                                        product_variation.append(variation)
                                except:
                                        pass
        
        # --------CART ITEM--------
                #try:
                is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()  # objects.create    #if cart item exists it will return true ,else false
                
                if is_cart_item_exists:  #try
                        cart_item = CartItem.objects.filter(product=product, user=current_user)
                        # existing variations -> database
                        # current variation -> product_variation
                        # item_id -> database
                        ex_var_list = []  #all variations list
                        id = []           #cart id
                        for item in cart_item:
                                existing_variation = item.variations.all()
                                ex_var_list.append(list(existing_variation))     #it is a query set, so we are converting to list using list() tag
                                id.append(item.id)

                        # current variation -> product_variation
                        if product_variation in ex_var_list:     
                                # increase cart item quantity
                                index = ex_var_list.index(product_variation)
                                item_id = id[index]
                                item = CartItem.objects.get(product=product, id=item_id)    # increase cart tem quantity
                                item.quantity += 1
                                item.save()
                        else:
                                item = CartItem.objects.create(product=product,quantity=1, user=current_user)  # create new cart item  
                                if len(product_variation) > 0:
                                        item.variations.clear()  #handling error of automatically adding products by having random variations while incrementing quantity
                                        item.variations.add(*product_variation)
                                item.save() 
                else:   #except CartItem.DoesNotExist:
                        cart_item = CartItem.objects.create(
                                product = product,
                                quantity = 1,
                                user=current_user,
                        )
                        if len(product_variation) > 0:
                                cart_item.variations.clear()
                                cart_item.variations.add(*product_variation) 
                        cart_item.save()

                return redirect('cart')    
#-------If user is not authenticated--------
        else:
        # ---------VARIATION--------
                product_variation = []
                if request.method == 'POST':
                        for item in request.POST:
                                key = item 
                                value = request.POST[key]
                                try:
                                        variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                                        product_variation.append(variation)
                                except:
                                        pass
        # -------CART-------
                try:
                        cart = Cart.objects.get(cart_id=_cart_id(request))
                except Cart.DoesNotExist:
                        cart = Cart.objects.create(
                                cart_id = _cart_id(request)
                        )
                cart.save()
        # --------CART ITEM--------
                #try:
                is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()  # objects.create    #if cart item exists it will return true ,else false
                if is_cart_item_exists:  #try
                        cart_item = CartItem.objects.filter(product=product, cart=cart)
                        # existing variations -> database
                        # current variation -> product_variation
                        # item_id -> database
                        ex_var_list = []
                        id = [] 
                        for item in cart_item:
                                existing_variation = item.variations.all()
                                ex_var_list.append(list(existing_variation))     #it is a quer set, so we are converting to list using list() tag
                                id.append(item.id)

                        print(ex_var_list)

                        # current variation -> product_variation
                        if product_variation in ex_var_list:
                                index = ex_var_list.index(product_variation)
                                item_id = id[index]
                                item = CartItem.objects.get(product=product, id=item_id)    # increase cart tem quantity
                                item.quantity += 1
                                item.save()
                        else:
                                item = CartItem.objects.create(product=product,quantity=1, cart=cart)  # create new cart item  
                                if len(product_variation) > 0:
                                        item.variations.clear()  #handling error of automatically adding products by having random variations while incrementing quantity
                                        item.variations.add(*product_variation)
                                item.save() 
                else:   #except CartItem.DoesNotExist:
                        cart_item = CartItem.objects.create(
                                product = product,
                                quantity = 1,
                                cart=cart,
                        )
                        if len(product_variation) > 0:
                                cart_item.variations.clear()
                                cart_item.variations.add(*product_variation) 
                        cart_item.save()

                return redirect('cart')    

def remove_cart(request,product_id, cart_item_id):  #decrements quantity
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:   
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass    
    
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart= Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):  
        try:
                tax = 0
                grand_total = 0
                if request.user.is_authenticated:
                        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
                else:
                        cart = Cart.objects.get(cart_id=_cart_id(request))
                        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                for cart_item in cart_items:
                        total    += (cart_item.product.price * cart_item.quantity)
                        quantity += cart_item.quantity
                tax = (2 * total)/100
                grand_total = total + tax
                
        except ObjectDoesNotExist:
                pass #just ignore
    
        context = {
                'total':total,
                'quantity':quantity,
                'cart_items':cart_items,
                'tax' : tax,
                'grand_total' : grand_total,
        }
        return render(request,'store/cart.html',context)


@login_required(login_url='signin')
def checkout(request, total=0, quantity=0, cart_items=None):
        user = request.user
        add = UserProfile.objects.filter(user=user)
        try:
                tax = 0
                grand_total = 0
                if request.user.is_authenticated:
                        cart_items = CartItem.objects.filter(user=request.user, is_active=True)  #cart = Cart.objects.get(cart_id=_cart_id(request))
                else:
                        cart = Cart.objects.get(cart_id=_cart_id(request))                       #cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                
                for cart_item in cart_items:
                        total    += (cart_item.product.price * cart_item.quantity)
                        quantity += cart_item.quantity
                tax = (2 * total)/100
                grand_total = total + tax
        except ObjectDoesNotExist:
                pass #just ignore
    
        context = {
                'total':total,
                'quantity':quantity,
                'cart_items':cart_items,
                'tax' : tax,
                'grand_total' : grand_total,
                'add' : add
        }

        return render(request, 'store/checkout.html', context)

