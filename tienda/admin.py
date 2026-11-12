from django.contrib import admin

from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'categoria', 'precio', 'stock', 'es_nuevo', 'fecha_lanzamiento')
    list_filter = ('categoria', 'es_nuevo', 'marca')
    search_fields = ('nombre', 'marca', 'especificaciones')
    list_editable = ('stock', 'es_nuevo')
    date_hierarchy = 'fecha_lanzamiento'
