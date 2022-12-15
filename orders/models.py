from django.db import models

from accounts.models import Account
from store.models import Product, Variation
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=130,blank=True)
    order_number = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=100, default='RazorPay')
    amount_paid = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
      return self.payment_id

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    minimum_amount = models.IntegerField(default=999)
    discount_price = models.IntegerField(default=199)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modify_date = models.DateTimeField(auto_now=True)
    expiry_at = models.DateTimeField(blank=True, null=True) 

    def __str__(self):
        return self.coupon_code

class Order(models.Model):
    STATUS = (
      ('New', 'New'),
      ('Order Accepted', 'Order Accepted'),
      ('Delivered Successfully', 'Delivered Successfully'),
      ('Order Cancelled', 'Order Cancelled'),
    )
    
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)  
    order_number = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200) 
    zipcode = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=250, blank=True) 
    order_total = models.FloatField()
    tax = models.FloatField()
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    coupon_discount = models.IntegerField(null=True)
    status = models.CharField(max_length=55, choices=STATUS, default='New')
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def full_name(self):
      return f'{self.firstname} {self.lastname}'
    
    def full_address(self):
      return f'{self.address_line_1} {self.address_line_2}'  # f' -> formating string
    
    def __str__(self):
      return self.order_number
  

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # def __str__(self):
    #   return self.order.order_number
    def __str__(self):
      return self.product.product_name
