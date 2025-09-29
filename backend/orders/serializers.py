from rest_framework import serializers
from .models import Order, OrderItem
class OrderItemSer(serializers.ModelSerializer):
    class Meta: model = OrderItem; fields = ['product','qty','unit_price','total']
class OrderSer(serializers.ModelSerializer):
    items = OrderItemSer(many=True)
    class Meta: model = Order; fields = ['id','code','subtotal','shipping_fee','total','status','items','created_at','updated_at']
