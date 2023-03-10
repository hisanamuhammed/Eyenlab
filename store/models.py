from django.db import models
from accounts.models import Account
from category.models import Category 
from django.db.models import Avg
from django.urls import reverse
from PIL import Image

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    images = models.ImageField(upload_to='photos/products')

    # def save(self, *args, **kwargs):
    #     img = Image.open(self.images.name)
    #     if img.height > 400 or img.width > 400:
    #         output_size = (350, 350)
    #         img.thumbnail(output_size)
    #         img.save(self.images.name)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


    def __str__(self):
        return self.product_name

# class VariationManager(models.Model):
#     def colors(self):
#         return super(VariationManager, self).filter(variation_category='color',is_active=True)
    
#     def size(self):
#         return super(VariationManager, self).filter(variation_category='size',is_active=True)

class VariationsManager(models.Manager):
    def colors(self):
        return super(VariationsManager, self).filter(variation_category='color',is_active=True)
    
    def sizes(self):
        return super(VariationsManager, self).filter(variation_category='size',is_active=True)


variation_category_choice = (   
    ('color','color'),
    ('size','size'),
)

class Variation(models.Model):
    product            = models.ForeignKey(Product, on_delete=models.CASCADE)  
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value    = models.CharField(max_length=100)
    is_active          = models.BooleanField(default=True)
    created_date       = models.DateTimeField(auto_now=True)

    objects = VariationsManager()

    def __str__(self):
        return self.variation_value


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image =models.ImageField(upload_to='store/products',max_length=255)
    
    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name='productgallery'   # change name productgallerys
        verbose_name_plural ='product gallery'
    



    # def averageReview(self):
    #     reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
    #     count = 0
    #     if reviews['count'] is not None:
    #         count = int(reviews['count'])
    #     return count

    
# class ReviewRating(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     user = models.ForeignKey(Account, on_delete=models.CASCADE)
#     subject = models.CharField(max_length=100, blank=True)
#     review = models.TextField(max_length=500, blank=True)
#     rating = models.FloatField()
#     ip = models.CharField(max_length=20,blank=True)
#     status = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
    
#     def str(self):
#         return self.subject