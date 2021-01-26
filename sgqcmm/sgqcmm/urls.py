from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', include('main.urls')),
    path('clientes/', include('clie.urls')),
    path('orcs/', include('orcs.urls')),
    path('procs/', include('proc.urls')),
    path('admin/', admin.site.urls),
]
