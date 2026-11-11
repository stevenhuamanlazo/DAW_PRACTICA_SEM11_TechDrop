from django.shortcuts import render
from django.views.generic import ListView

from .models import Producto


def home(request):
    contexto = {
        'titulo': 'TechDrop',
        'eslogan': 'Hardware y gadgets para devs',
    }
    return render(request, 'tienda/home.html', contexto)


class CatalogoView(ListView):
    model = Producto
    template_name = 'tienda/catalogo.html'
    context_object_name = 'productos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Catálogo'
        context['total'] = self.object_list.count()
        return context
