from django.urls import path
from .api import create_order
urlpatterns = [ path('api/create', create_order, name='order_create') ]
