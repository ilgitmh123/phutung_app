from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BrandVS, CategoryVS, VehicleModelVS, ProductVS, import_json_api
from .views import home, product_list, product_detail

router = DefaultRouter()
router.register(r"brands", BrandVS)
router.register(r"categories", CategoryVS)
router.register(r"models", VehicleModelVS)
router.register(r"products", ProductVS)

urlpatterns = [
    path('', home, name='home'),
    path('shop/', product_list, name='product_list'),
    path('p/<slug:slug>/', product_detail, name='product_detail'),
    path('api/', include(router.urls)),
    path('api/import/json', import_json_api, name='import_json_api'),
]
