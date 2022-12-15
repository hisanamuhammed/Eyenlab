from . import views
from django.urls import path

urlpatterns = [
    path('signin/',views.signin, name='signin'),
    path('signup/',views.signup, name='signup'),
    path('signout/',views.signout, name='signout'),

    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetPassword_validate, name='resetPassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

    path('dashboard/',views.dashboard, name='dashboard'),
    path('my_orders/', views.my_orders, name='my_orders'),

    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('address/', views.address, name='address'),
    
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    path('user_cancel_order/<int:order_number>/', views.user_cancel_order, name='user_cancel_order'),
    path('user_manage_order/', views.user_manage_order, name='user_manage_order'),

]