from datetime import date

from django.core.management.base import BaseCommand

from tienda.models import Producto

# (nombre, marca, categoria, especificaciones, precio, stock, fecha_lanzamiento, es_nuevo)
DATOS = [
    ("teclado mecanico k2", "Keychron", "perifericos", "75% - Switch Brown - Bluetooth 5.1", 329.90, 12, date(2026, 10, 20), True),
    ("mouse inalambrico mx master", "Logitech", "perifericos", "4000 DPI - USB-C - 70 dias de bateria", 349.00, 4, date(2026, 9, 5), False),
    ("audifonos gamer cloud ii", "HyperX", "perifericos", "7.1 virtual - Microfono desmontable - USB", 299.00, 0, date(2026, 4, 18), False),
    ("ssd nvme 1tb", "Samsung", "componentes", "NVMe Gen4 - 7000 MB/s lectura", 289.50, 20, date(2026, 8, 15), False),
    ("memoria ram ddr5 32gb", "Corsair", "componentes", "2x16GB - 6000MHz - CL30", 459.00, 0, date(2026, 7, 1), False),
    ("tarjeta grafica rtx 4060", "Gigabyte", "componentes", "8GB GDDR6 - DLSS 3 - 3 ventiladores", 1399.00, 2, date(2026, 11, 5), True),
    ("router wifi 6 ax3000", "TP-Link", "redes", "WiFi 6 - 4 antenas - Gigabit", 219.00, 8, date(2026, 6, 12), False),
    ("switch gigabit 8 puertos", "TP-Link", "redes", "8 puertos 10/100/1000 - Sin gestion", 79.90, 0, date(2026, 5, 3), False),
    ("cable utp cat6 30m", "Ugreen", "redes", "Cat6 - 30 metros - Conectores RJ45", 45.00, 25, date(2026, 3, 9), False),
    ("raspberry pi 5 8gb", "Raspberry Pi", "iot", "Quad-core 2.4GHz - 8GB RAM - WiFi 5", 389.00, 3, date(2026, 11, 2), True),
    ("arduino uno r4 wifi", "Arduino", "iot", "Renesas RA4M1 - WiFi - Matriz LED", 119.00, 15, date(2026, 10, 28), True),
    ("esp32 devkit v1", "Espressif", "iot", "Dual-core 240MHz - WiFi y Bluetooth - 30 pines", 38.00, 40, date(2026, 2, 14), False),
]


class Command(BaseCommand):
    help = "Carga productos de prueba con el ORM. Se puede ejecutar varias veces sin duplicar datos."

    # IA: OperationalError "no such table: tienda_producto" → Solución manual: ejecutar makemigrations y migrate antes de consultar el modelo
    def handle(self, *args, **options):
        creados = 0
        for nombre, marca, categoria, specs, precio, stock, fecha, nuevo in DATOS:
            _, fue_creado = Producto.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'marca': marca,
                    'categoria': categoria,
                    'especificaciones': specs,
                    'precio': precio,
                    'stock': stock,
                    'fecha_lanzamiento': fecha,
                    'es_nuevo': nuevo,
                },
            )
            creados += fue_creado
        self.stdout.write(self.style.SUCCESS(
            f"Productos creados: {creados} · Total en inventario: {Producto.objects.count()}"
        ))
