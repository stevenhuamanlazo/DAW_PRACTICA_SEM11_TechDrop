from django.urls import path
from . import views

app_name = 'tienda'

# IA: 404 al abrir /home → Solución manual: el inicio es la ruta '' (raíz); 'home' es solo el name para {% url %}
urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.CatalogoView.as_view(), name='catalogo'),
    path('inventario/', views.InventarioView.as_view(), name='inventario'),
    path('producto/<int:pk>/', views.DetalleView.as_view(), name='detalle'),
]
