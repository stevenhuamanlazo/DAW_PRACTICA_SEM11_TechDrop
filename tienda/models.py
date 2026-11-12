from django.contrib.staticfiles import finders
from django.db import models
from django.db.models import Avg, Count, DecimalField, F, Max, Min, Q, Sum
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify

# Extensiones aceptadas para la foto de cada producto
EXTENSIONES_IMAGEN = ('jpg', 'jpeg', 'png', 'webp')

# Para sumar precio * stock hay que indicar el tipo del resultado
VALOR = DecimalField(max_digits=12, decimal_places=2)


class ProductoQuerySet(models.QuerySet):
    """Consultas reutilizables del inventario.

    La lógica de filtrado y de cálculo vive aquí (en el modelo) y no en las vistas,
    como pide la guía: "Delegar a modelos o servicios".
    Los QuerySets son lazy: no tocan la base de datos hasta que se evalúan.
    """

    # ---- filtros encadenables ----
    def disponibles(self):
        return self.filter(stock__gt=0)

    def agotados(self):
        return self.filter(stock=0)

    def stock_bajo(self):
        return self.filter(stock__gt=0, stock__lte=Producto.STOCK_BAJO)

    def nuevos(self):
        return self.filter(es_nuevo=True)

    def de_categoria(self, categoria):
        return self.filter(categoria=categoria)

    def buscar(self, texto):
        return self.filter(
            Q(nombre__icontains=texto)
            | Q(marca__icontains=texto)
            | Q(especificaciones__icontains=texto)
        )

    # ---- agregaciones (aggregate / annotate) ----
    def resumen_categorias(self):
        """Lista de dicts [{'clave', 'nombre', 'cantidad'}] con el conteo por categoría."""
        conteos = dict(
            self.order_by().values_list('categoria').annotate(n=Count('id'))
        )
        return [
            {'clave': clave, 'nombre': nombre, 'cantidad': conteos.get(clave, 0)}
            for clave, nombre in Producto.CATEGORIAS
        ]

    def estadisticas(self):
        """Totales del inventario en una sola consulta (aggregate)."""
        return self.aggregate(
            productos=Count('id'),
            unidades=Sum('stock'),
            valor_total=Sum(F('precio') * F('stock'), output_field=VALOR),
            precio_promedio=Avg('precio'),
            precio_max=Max('precio'),
            precio_min=Min('precio'),
        )

    def por_categoria(self):
        """Productos, unidades y valor por categoría (annotate) con su porcentaje del total."""
        filas = list(
            self.order_by()
            .values('categoria')
            .annotate(
                productos=Count('id'),
                unidades=Sum('stock'),
                valor=Sum(F('precio') * F('stock'), output_field=VALOR),
            )
            .order_by('categoria')
        )
        nombres = dict(Producto.CATEGORIAS)
        total = sum(f['valor'] or 0 for f in filas)
        for f in filas:
            f['nombre'] = nombres.get(f['categoria'], f['categoria'])
            f['porcentaje'] = round(float(f['valor'] or 0) / float(total) * 100) if total else 0
        return filas

    def mas_caro(self):
        return self.order_by('-precio').first()

    def mas_barato(self):
        return self.order_by('precio').first()


class Producto(models.Model):
    CATEGORIAS = [
        ('perifericos', 'Periféricos'),
        ('componentes', 'Componentes'),
        ('redes', 'Redes'),
        ('iot', 'IoT y SBC'),
    ]

    # Umbral para mostrar "Últimas unidades" en el catálogo
    STOCK_BAJO = 5

    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    especificaciones = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    fecha_lanzamiento = models.DateField()
    es_nuevo = models.BooleanField(default=False)

    objects = ProductoQuerySet.as_manager()

    class Meta:
        ordering = ['-fecha_lanzamiento']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('tienda:detalle', args=[self.pk])

    @property
    def agotado(self):
        return self.stock == 0

    @property
    def pocas_unidades(self):
        return 0 < self.stock <= self.STOCK_BAJO

    @property
    def valor_en_stock(self):
        return self.precio * self.stock

    @cached_property
    def imagen_url(self):
        """Ruta static de la foto del producto, o None si no existe.

        Convención: tienda/static/tienda/img/productos/<nombre-en-slug>.<jpg|jpeg|png|webp>
        Ejemplo: 'teclado mecanico k2' → teclado-mecanico-k2.jpg
        """
        base = f'tienda/img/productos/{slugify(self.nombre)}'
        for ext in EXTENSIONES_IMAGEN:
            ruta = f'{base}.{ext}'
            if finders.find(ruta):
                return ruta
        return None
