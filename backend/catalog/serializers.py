from rest_framework import serializers
from .models import Brand, Category, VehicleModel, Product

class BrandSer(serializers.ModelSerializer):
    class Meta: model = Brand; fields = "__all__"

class CategorySer(serializers.ModelSerializer):
    class Meta: model = Category; fields = "__all__"

class VehicleModelSer(serializers.ModelSerializer):
    brand = BrandSer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), source="brand", write_only=True)
    class Meta: model = VehicleModel; fields = ["id","brand","brand_id","name","year_from","year_to","engine_cc","notes"]

class ProductSer(serializers.ModelSerializer):
    brand = BrandSer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), source="brand", write_only=True)
    category = CategorySer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category", write_only=True, allow_null=True)
    class Meta:
        model = Product
        fields = ["id","sku","oem_code","name","slug","brand","brand_id","category","category_id","description","attributes","specs","retail_price","sale_price","stock_on_hand","stock_reserved","reorder_point","status","meta_title","meta_description","is_featured","created_at","updated_at"]
