from django.contrib import admin
from .models import Brand, Category, VehicleModel, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku","name","brand","category","retail_price","stock_on_hand","status")
    search_fields = ("sku","name","oem_code")
    list_filter = ("brand","category","status")

admin.site.register([Brand, Category, VehicleModel])
