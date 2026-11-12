from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Producto


def crear(nombre, categoria='perifericos', stock=10, nuevo=False, precio=100, marca='Marca'):
    return Producto.objects.create(
        nombre=nombre, marca=marca, categoria=categoria, especificaciones='specs de prueba',
        precio=precio, stock=stock, fecha_lanzamiento=date(2026, 1, 1), es_nuevo=nuevo,
    )


class ModeloTests(TestCase):
    def setUp(self):
        self.teclado = crear('teclado k2', 'perifericos', stock=10, nuevo=True, marca='Keychron')
        self.router = crear('router ax', 'redes', stock=0)
        self.pi = crear('raspberry pi', 'iot', stock=3, nuevo=True)

    def test_str_devuelve_el_nombre(self):
        self.assertEqual(str(self.teclado), 'teclado k2')

    def test_queryset_disponibles_y_agotados(self):
        self.assertEqual(Producto.objects.disponibles().count(), 2)
        self.assertEqual(list(Producto.objects.agotados()), [self.router])

    def test_queryset_nuevos_y_categoria(self):
        self.assertEqual(Producto.objects.nuevos().count(), 2)
        self.assertEqual(list(Producto.objects.de_categoria('redes')), [self.router])

    def test_buscar_por_nombre_y_marca(self):
        self.assertEqual(list(Producto.objects.buscar('keychron')), [self.teclado])
        self.assertEqual(list(Producto.objects.buscar('RASPBERRY')), [self.pi])

    def test_propiedades_de_stock(self):
        self.assertTrue(self.router.agotado)
        self.assertTrue(self.pi.pocas_unidades)
        self.assertFalse(self.teclado.pocas_unidades)

    def test_resumen_categorias_incluye_todas(self):
        resumen = {c['clave']: c['cantidad'] for c in Producto.objects.resumen_categorias()}
        self.assertEqual(resumen, {'perifericos': 1, 'componentes': 0, 'redes': 1, 'iot': 1})


class VistasTests(TestCase):
    def setUp(self):
        self.teclado = crear('teclado k2', 'perifericos', stock=10, nuevo=True, precio=300)
        self.router = crear('router ax', 'redes', stock=0, precio=200)
        self.pi = crear('raspberry pi', 'iot', stock=3, precio=400)

    def test_home_responde_200_y_usa_plantilla(self):
        r = self.client.get(reverse('tienda:home'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'tienda/home.html')
        self.assertTemplateUsed(r, 'tienda/base.html')
        self.assertEqual(r.context['total'], 3)

    def test_catalogo_lista_todos(self):
        r = self.client.get(reverse('tienda:catalogo'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['productos']), 3)
        self.assertContains(r, 'Teclado K2')  # filtro |title

    def test_catalogo_filtra_por_categoria(self):
        r = self.client.get(reverse('tienda:catalogo'), {'categoria': 'redes'})
        self.assertEqual(list(r.context['productos']), [self.router])

    def test_catalogo_ignora_categoria_invalida(self):
        r = self.client.get(reverse('tienda:catalogo'), {'categoria': 'inventada'})
        self.assertEqual(len(r.context['productos']), 3)

    def test_catalogo_busqueda_y_disponibles(self):
        r = self.client.get(reverse('tienda:catalogo'), {'q': 'router'})
        self.assertEqual(list(r.context['productos']), [self.router])
        r = self.client.get(reverse('tienda:catalogo'), {'disponibles': '1'})
        self.assertNotIn(self.router, r.context['productos'])

    def test_catalogo_ordena_por_precio(self):
        r = self.client.get(reverse('tienda:catalogo'), {'orden': 'precio_desc'})
        self.assertEqual([p.precio for p in r.context['productos']], [400, 300, 200])

    def test_catalogo_sin_resultados_muestra_mensaje(self):
        r = self.client.get(reverse('tienda:catalogo'), {'q': 'zzzz'})
        self.assertContains(r, 'No encontramos productos')

    def test_detalle_ok_y_404(self):
        r = self.client.get(reverse('tienda:detalle', args=[self.teclado.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Teclado K2')
        r = self.client.get(reverse('tienda:detalle', args=[9999]))
        self.assertEqual(r.status_code, 404)

    def test_urls_reversibles_por_name(self):
        self.assertEqual(reverse('tienda:home'), '/')
        self.assertEqual(reverse('tienda:catalogo'), '/catalogo/')
