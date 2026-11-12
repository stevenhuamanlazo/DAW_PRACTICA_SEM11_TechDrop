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


class AgregacionesTests(TestCase):
    """aggregate() y annotate() sobre el inventario."""

    def setUp(self):
        crear('teclado k2', 'perifericos', stock=10, precio=300)   # valor 3000
        crear('router ax', 'redes', stock=0, precio=200)           # valor 0
        crear('raspberry pi', 'iot', stock=3, precio=400)          # valor 1200

    def test_estadisticas(self):
        e = Producto.objects.estadisticas()
        self.assertEqual(e['productos'], 3)
        self.assertEqual(e['unidades'], 13)
        self.assertEqual(e['valor_total'], 4200)
        self.assertEqual(e['precio_max'], 400)
        self.assertEqual(e['precio_min'], 200)

    def test_por_categoria_suma_100_por_ciento(self):
        filas = Producto.objects.por_categoria()
        self.assertEqual(sum(f['porcentaje'] for f in filas), 100)
        perifericos = next(f for f in filas if f['categoria'] == 'perifericos')
        self.assertEqual(perifericos['valor'], 3000)

    def test_extremos_y_stock_bajo(self):
        self.assertEqual(Producto.objects.mas_caro().nombre, 'raspberry pi')
        self.assertEqual(Producto.objects.mas_barato().nombre, 'router ax')
        self.assertEqual([p.nombre for p in Producto.objects.stock_bajo()], ['raspberry pi'])

    def test_vista_inventario(self):
        r = self.client.get(reverse('tienda:inventario'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'tienda/inventario.html')
        self.assertContains(r, 'S/ 4,200.00')
        self.assertEqual(r.context['mas_caro'].nombre, 'raspberry pi')


class TagsPersonalizadosTests(TestCase):
    def test_filtro_soles(self):
        from .templatetags.tienda_extras import soles
        self.assertEqual(soles(1399), 'S/ 1,399.00')
        self.assertEqual(soles(79.9), 'S/ 79.90')
        self.assertEqual(soles('texto'), 'texto')

    def test_filtro_estado_stock(self):
        from .templatetags.tienda_extras import estado_stock
        self.assertEqual(estado_stock(crear('a', stock=0)), 'Agotado')
        self.assertEqual(estado_stock(crear('b', stock=2)), 'Últimas 2')
        self.assertEqual(estado_stock(crear('c', stock=50)), 'En stock')

    def test_menu_de_categorias_sale_de_la_base_de_datos(self):
        r = self.client.get(reverse('tienda:home'))
        for clave in ('perifericos', 'componentes', 'redes', 'iot'):
            self.assertContains(r, f'?categoria={clave}')


class PaginacionTests(TestCase):
    def setUp(self):
        for i in range(10):
            crear(f'producto {i:02d}', 'iot', precio=10 + i)

    def test_primera_y_segunda_pagina(self):
        r1 = self.client.get(reverse('tienda:catalogo'))
        self.assertEqual(len(r1.context['productos']), 8)
        self.assertTrue(r1.context['is_paginated'])
        r2 = self.client.get(reverse('tienda:catalogo'), {'page': 2})
        self.assertEqual(len(r2.context['productos']), 2)

    def test_los_enlaces_conservan_los_filtros(self):
        r = self.client.get(reverse('tienda:catalogo'), {'categoria': 'iot', 'orden': 'precio_asc'})
        self.assertContains(r, 'page=2')
        self.assertContains(r, 'categoria=iot')


class ImagenTests(TestCase):
    def test_sin_foto_devuelve_none_y_usa_icono(self):
        p = crear('teclado sin foto')
        self.assertIsNone(p.imagen_url)
        r = self.client.get(reverse('tienda:detalle', args=[p.pk]))
        self.assertContains(r, 'class="icono"')

    def test_con_foto_usa_la_convencion_de_nombre(self):
        from unittest.mock import patch
        p = crear('Teclado Mecanico K2')
        with patch('tienda.models.finders.find', side_effect=lambda ruta: ruta.endswith('.png')):
            self.assertEqual(p.imagen_url, 'tienda/img/productos/teclado-mecanico-k2.png')
