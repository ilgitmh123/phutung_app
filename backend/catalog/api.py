from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from .models import Brand, Category, VehicleModel, Product
from .serializers import BrandSer, CategorySer, VehicleModelSer, ProductSer
import json, re

class BrandVS(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandSer

class CategoryVS(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySer

class VehicleModelVS(viewsets.ModelViewSet):
    queryset = VehicleModel.objects.select_related("brand").all()
    serializer_class = VehicleModelSer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["brand"]

class ProductVS(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("brand","category").all()
    serializer_class = ProductSer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["brand","category","status"]
    search_fields = ["name","sku","oem_code","meta_title","meta_description"]
    ordering_fields = ["retail_price","name","created_at"]

# Lightweight API upload JSON -> upsert (admin only)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_json_api(request):
    try:
        payload = request.data
        if isinstance(payload, (bytes,str)):
            data = json.loads(payload if isinstance(payload,str) else payload.decode('utf-8'))
        else:
            data = payload
        if not isinstance(data, dict):
            return Response({'error':'Expecting object keyed by SKU'}, status=400)
        ok, fail = 0,0
        from .utils_import import normalize_item  # helper defined below
        for sku, raw in data.items():
            try:
                normalized = normalize_item(sku, raw, default_brand="Honda")
                obj, created = Product.objects.get_or_create(sku=sku, defaults=normalized)
                if not created:
                    for k,v in normalized.items():
                        setattr(obj,k,v)
                    obj.save()
                ok+=1
            except Exception as e:
                fail+=1
        return Response({'ok':ok,'fail':fail})
    except Exception as e:
        return Response({'error':str(e)}, status=500)
