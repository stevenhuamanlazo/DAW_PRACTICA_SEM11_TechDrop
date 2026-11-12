from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Producto

# Ordenamientos permitidos en el catálogo (lista blanca: nunca se usa el texto del usuario tal cual)
ORDENES = {
    'reciente': ('Más recientes', '-fecha_lanzamiento'),
    'precio_asc': ('Precio: menor a mayor', 'precio'),
    'precio_desc': ('Precio: mayor a menor', '-precio'),
    'nombre': ('Nombre (A-Z)', 'nombre'),
}


# FBV: vista basada en función
# IA: TemplateDoesNotExist en "/" → Solución manual: la plantilla debe estar en tienda/templates/tienda/home.html
def home(request):
    contexto = {
        'titulo': 'TechDrop',
        'eslogan': 'Hardware y gadgets para devs',
        'nuevos': Producto.objects.nuevos()[:4],
        'categorias': Producto.objects.resumen_categorias(),
        'total': Producto.objects.count(),
        'disponibles': Producto.objects.disponibles().count(),
    }
    return render(request, 'tienda/home.html', contexto)


# CBV: vista basada en clase (ListView)
class CatalogoView(ListView):
    model = Producto
    template_name = 'tienda/catalogo.html'
    context_object_name = 'productos'

    def get_queryset(self):
        # Los filtros viven en el QuerySet del modelo; aquí solo se encadenan.
        qs = super().get_queryset()
        categoria = self.request.GET.get('categoria', '')
        texto = self.request.GET.get('q', '').strip()
        orden = self.request.GET.get('orden', 'reciente')

        if categoria in dict(Producto.CATEGORIAS):
            qs = qs.de_categoria(categoria)
        if texto:
            qs = qs.buscar(texto)
        if self.request.GET.get('disponibles'):
            qs = qs.disponibles()
        return qs.order_by(ORDENES.get(orden, ORDENES['reciente'])[1])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Catálogo'
        context['total'] = self.object_list.count()
        context['categorias'] = Producto.objects.resumen_categorias()
        context['ordenes'] = [(clave, datos[0]) for clave, datos in ORDENES.items()]
        context['categoria_activa'] = self.request.GET.get('categoria', '')
        context['q'] = self.request.GET.get('q', '').strip()
        context['orden_activo'] = self.request.GET.get('orden', 'reciente')
        context['solo_disponibles'] = bool(self.request.GET.get('disponibles'))
        return context


class DetalleView(DetailView):
    model = Producto
    template_name = 'tienda/detalle.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.object.nombre
        context['relacionados'] = (
            Producto.objects.de_categoria(self.object.categoria)
            .exclude(pk=self.object.pk)[:3]
        )
        return context
