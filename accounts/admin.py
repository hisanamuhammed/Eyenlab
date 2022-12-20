from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import Account, UserProfile
from django.utils.html import format_html


class AccountAdmin(UserAdmin):
    list_display = ('first_name','last_name','username','email','phone_number','date_joined', 'is_active')
    list_display_links = ('email','first_name','last_name','username')
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',) # - here represents it will show in the descending order
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()     #this will make the pass readonly in adminpanel


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):       # image function
        return format_html('<img src="{}" width="30" style="border-radius:50;">'.format(object.profile_picture.url))
    thumbnail.short_discription = 'Profile Picture' # this will be shown in the database
    list_display = ('thumbnail', 'user', 'city', 'state', 'pin')    
    
# Register your models here.

admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)



