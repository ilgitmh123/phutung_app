import json

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Product

def home(request):
    qs = Product.objects.order_by('-created_at')[:8]
    return render(request, 'home.html', { 'featured': qs })

def product_list(request):
    q = request.GET.get('q','').strip()
    qs = Product.objects.select_related('brand','category').all()
    if q:
        qs = qs.filter(Q(name__icontains=q)|Q(sku__icontains=q)|Q(oem_code__icontains=q))
    paginator = Paginator(qs, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'catalog/list.html', { 'page_obj': page_obj, 'q': q })

def product_detail(request, slug):
    p = get_object_or_404(Product, slug=slug)
    attributes_pretty = json.dumps(p.attributes, ensure_ascii=False, indent=2)
    return render(request, 'catalog/detail.html', {
        'p': p,
        'attributes_pretty': attributes_pretty,
    })
