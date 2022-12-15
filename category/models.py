from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    # description = models.TextField(max_length=250, blank=True)
    # cat_image = models.ImageField(upload_to='photos/categories', null=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'  # To get the name 'categories' for this model in admin panel, instead of 'categorys'(default) 

    def __str__(self):
        return self.category_name

    def get_url(self):
        return reverse('products_by_category',args=[self.slug])  #this function will take to url of particular category]