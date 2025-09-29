from django.db import models
from django.conf import settings
from catalog.models import Product
class Order(models.Model):
    NEW, PAID, SHIPPED, DONE, CANCELLED = ('NEW','PAID','SHIPPED','DONE','CANCELLED')
    STATUS_CHOICES = [(NEW,NEW),(PAID,PAID),(SHIPPED,SHIPPED),(DONE,DONE),(CANCELLED,CANCELLED)]
    code = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    subtotal = models.BigIntegerField(default=0)
    shipping_fee = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.IntegerField(default=1)
    unit_price = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
