# models.py

from django.db import models
from django.contrib.auth.models import User as DjangoUser

class UserProfile(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE)
    is_super_user = models.BooleanField(default=False)


class Address(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)


class Product(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    quantity = models.IntegerField()
    is_listed = models.BooleanField(default=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/') 

    def __str__(self):
        return f"Image for {self.product.name}"
    

class Cart(models.Model):
    user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('DELIVERED', 'Delivered'),
    ]

    user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')

class AdminOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)



