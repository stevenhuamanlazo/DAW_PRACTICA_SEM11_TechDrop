from django.db import models
from django.db.models import Count, Q
from django.urls import reverse


class ProductoQuerySet(models.QuerySet):
    """Consultas reutilizables del inventario.

    La lógica de filtrado vive aquí (en el modelo) y no en las vistas,
    como pide la guía: "Delegar a modelos o servicios".
    Los QuerySets son lazy: no tocan la base de datos hasta que se evalúan.
    """

    def disponibles(self):
        return self.filter(stock__gt=0)

    def agotados(self):
        return self.filter(stock=0)

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

    def resumen_categorias(self):
        """Lista de dicts [{'clave', 'nombre', 'cantidad'}] con el conteo por categoría."""
        conteos = dict(
            self.order_by().values_list('categoria').annotate(n=Count('id'))
        )
        return [
            {'clave': clave, 'nombre': nombre, 'cantidad': conteos.get(clave, 0)}
            for clave, nombre in Producto.CATEGORIAS
        ]


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
