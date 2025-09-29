from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('', include('catalog.urls')),
    path('auth/', include('users.urls')),
    path('orders/', include('orders.urls')),
]

# 👇 thêm dòng này bên ngoài list, KHÔNG chèn trong []
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
