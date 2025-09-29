import random, string
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from catalog.models import Product
from .serializers import OrderSer

def _gen_code():
    return ''.join(random.choices(string.ascii_uppercase+string.digits, k=8))

@api_view(['POST'])
def create_order(request):
    data = request.data or {}
    items = data.get('items', [])
    if not items:
        return Response({'error':'items required'}, status=400)
    order = Order.objects.create(code=_gen_code())
    subtotal = 0
    for it in items:
        sku = it.get('sku')
        qty = int(it.get('qty',1))
        try:
            p = Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return Response({'error':f'Product {sku} not found'}, status=404)
        unit = p.sale_price or p.retail_price
        total = unit * qty
        OrderItem.objects.create(order=order, product=p, qty=qty, unit_price=unit, total=total)
        subtotal += total
    order.subtotal = subtotal
    order.total = subtotal + order.shipping_fee
    order.save()
    return Response(OrderSer(order).data, status=201)
