# Pruebas del CRUD

## Ejecutar

Desde la raiz del proyecto, con el entorno virtual instalado:

```bash
venv/bin/pip install -r requirements-dev.txt
venv/bin/pytest -q --disable-warnings
```

Las pruebas usan SQLite en memoria de forma predeterminada, con claves foraneas activadas. No escriben en la base diaria de PostgreSQL. Cada prueba prepara sus registros y revierte su transaccion.

## Cobertura

- tests/test_crud.py: crear, listar con paginas, detalle, editar, desactivar, duplicados, campos invalidos, datos opcionales y limites entre empresas.
- tests/test_pivotes.py: catalogos conocidos, servicios y pagos por sucursal, vinculos laborales, asignaciones y disponibilidad de productos.
- tests/conftest.py: base aislada, datos y cliente de la API.

Para PostgreSQL se puede definir TEST_DATABASE_URL apuntando exclusivamente a una base de pruebas. La preparacion ejecuta create_all para las tablas faltantes; no usar la base de produccion o de trabajo diario para esta opcion. Las pruebas no sustituyen las migraciones.

## Migraciones

```bash
venv/bin/alembic upgrade head
venv/bin/alembic current
venv/bin/alembic check
```

La revision 0ac89592a3e5 agrega disponibilidad_productos y las restricciones de nombre unico por empresa de categorias y productos.

Los avisos sobre datetime.utcnow provienen de valores predeterminados de modelos existentes. No significan que las pruebas hayan fallado; su modernizacion queda fuera de este cambio.
