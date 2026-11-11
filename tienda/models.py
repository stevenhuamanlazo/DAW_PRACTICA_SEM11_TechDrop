from django.db import models


class Producto(models.Model):
    CATEGORIAS = [
        ('perifericos', 'Periféricos'),
        ('componentes', 'Componentes'),
        ('redes', 'Redes'),
        ('iot', 'IoT y SBC'),
    ]

    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    especificaciones = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    fecha_lanzamiento = models.DateField()
    es_nuevo = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_lanzamiento']

    def __str__(self):
        return self.nombre
