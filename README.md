# TechDrop · catálogo e inventario de hardware para devs

Práctica Semana 11 · Desarrollo de Aplicaciones Web (IS093A) · Ingeniería de Sistemas, UNCP.

Aplicación web hecha con **Django 5.2** y **SQLite** que aplica el patrón **MTV** (Model-Template-View):
catálogo de teclados, componentes, redes y placas IoT, con control de stock, filtros, búsqueda y ficha de producto.

## Cómo ejecutarlo (Windows / PowerShell)

```powershell
git clone https://github.com/stevenhuamanlazo/DAW_PRACTICA_SEM11_TechDrop.git
cd DAW_PRACTICA_SEM11_TechDrop
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py cargar_datos
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>. La base `db.sqlite3` no se sube al repositorio, por eso se genera con `migrate` y se llena con `cargar_datos` (usa el ORM y se puede repetir sin duplicar datos).

Pruebas automáticas: `python manage.py test`

## Rutas

| URL | Vista | name |
|---|---|---|
| `/` | `home` (FBV) | `tienda:home` |
| `/catalogo/` | `CatalogoView` (CBV, `ListView`) | `tienda:catalogo` |
| `/producto/<id>/` | `DetalleView` (CBV, `DetailView`) | `tienda:detalle` |
| `/admin/` | Admin de Django | |

El catálogo acepta `?categoria=`, `?q=`, `?orden=` y `?disponibles=1`.

## Qué se aplica de la guía

- **Rutas:** `config/urls.py` incluye `tienda/urls.py` con `include()`; todas con `name` y en las plantillas solo se usa `{% url %}`.
- **Vistas:** una FBV (`home`) y CBV (`ListView`, `DetailView`) con `get_context_data()`. Sin lógica de negocio: el filtrado vive en el QuerySet del modelo.
- **Plantillas:** `base.html` con bloques; `catalogo.html`, `home.html` y `detalle.html` con `{% extends %}`, `{% for %}`/`{% empty %}`, `{% if %}`/`{% elif %}`, `{% include %}` y filtros (`title`, `date`, `upper`, `truncatechars`, `floatformat`, `pluralize`).
- **Modelo:** `Producto` con `__str__`, migraciones y un `QuerySet` propio (`disponibles()`, `nuevos()`, `de_categoria()`, `buscar()`), que aprovecha la evaluación lazy de los QuerySets.
- **Estructura lista para la Semana 12:** el modelo ya está en el admin con `list_display`, filtros y búsqueda.

## Notas

- `DEBUG = True` solo para desarrollo; no usar así en producción.
- No se ignoran los avisos de *unapplied migrations*: se corre `python manage.py migrate`.
- `db.sqlite3` está en `.gitignore`.

## Uso de IA

La IA se usó como apoyo para entender y depurar errores. Cada caso está marcado en el código con `# IA: [problema] → Solución manual: [explicación]`:
`TemplateDoesNotExist` (`tienda/views.py`), 404 en `/home` (`tienda/urls.py`) y `no such table` (`tienda/management/commands/cargar_datos.py`).
