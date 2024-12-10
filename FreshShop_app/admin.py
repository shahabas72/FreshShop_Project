from django.contrib import admin

# Register your models here.
from .models import Cart, Product

admin.site.register(Product)
admin.site.register(Cart)