from django.urls import path
from .views import *

urlpatterns = [
  path('', redirect_to_login),
  path('login', manager_login, name='manager_login'),
  path('logout', manager_logout, name='manager_logout'),

  path('dashboard', manager_dashboard, name='manager_dashboard'),

  path('manage_user', manage_user, name='manage_user'),
  path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
  path('unban_user/<int:user_id>/', unban_user, name='unban_user'),

  path('manage_category/', manage_category, name='manage_category'),
  path('add_category/', add_category, name='add_category'),
  path('delete_category/<int:category_id>/', delete_category, name="delete_category"),

  path('manage_product/', manage_product, name='manage_product'),
  path('edit_product/<int:product_id>/', edit_product, name='edit_product'),
  path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
  path('add_product/', add_product, name='add_product'), 

  path('manage_variation/', manage_variation, name='manage_variation'),
  path('delete_variation/<int:variation_id>/', delete_variation, name='delete_variation'),
  path('update_variation/<int:variation_id>/', update_variation, name='update_variation'),
  path('add_variation/', add_variation, name='add_variation'),
  
  path('manage_order/', manage_order, name='manage_order'),
  path('admin_cancel_order/<int:order_number>/', cancel_order, name='admin_cancel_order'),
  path('accept_order/<int:order_number>/', accept_order, name='accept_order'),
  path('complete_order/<int:order_number>/', complete_order, name='complete_order'),
  path('admin_orders/', admin_order, name='admin_orders'),

  #coupon_management
  path('coupon_management/',coupon_management, name="coupon_management"),
  path('add_coupon', add_coupon, name="add_coupon"),
  path('update_coupon/<int:coupon_id>/', update_coupon, name="update_coupon"),
  path('delete_coupon/<int:coupon_id>/', delete_coupon, name="delete_coupon"),

  path('manage_sales', manage_sales, name="manage_sales"),
  path('create-pdf', pdf_report_create,name='create-pdf'),
  path('create-csv', csv_report_create,name='create-csv'),
]

#   path('change_password/', admin_change_password, name='admin_change_password'),



