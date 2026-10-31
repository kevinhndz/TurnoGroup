import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. ASEGURAR QUE PYTHON ENCUENTRE LOS MODULOS EN LA RAIZ DEL PROYECTO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. IMPORTAR LA INSTANCIA DE CONFIGURACION (revision) Y LA BASE DE DATOS
from core.config import revision
from database.almacen import miclaseBase

# 3. IMPORTAR MANUALMENTE Los MODELOS/TABLAS A MEDIDA QUE SE VAYA CREANDO CADA ENTIDAD
from backend.Empresas.tabla import Empresas  # Registra la tabla en metadata.
from backend.Categorias.tabla import Categorias
from backend.Productos.tabla import Productos
from backend.Usuarios.tabla import Usuarios
from backend.Sucursales.tabla import Sucursales
from backend.VinculosLaborales.tabla import VinculosLaborales, AsignacionesSucursales
from backend.Mesas.tabla import Mesas
from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
from backend.Descuentos.tabla import Descuentos
from backend.TiposServicio.tabla import TiposServicio
from backend.MetodosPago.tabla import MetodosPago
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.PagosSucursales.tabla import PagosSucursales
from backend.CategoriasGastos.tabla import CategoriasGastos

#EJEMPLOS  FUTUROS:
# from backend.empresas.model import Empresa
# from backend.productos.model import Producto
# from backend.finanzas.model import Finanza

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. INYECTAR LA URL DE LA BASE DE DATOS DESDE EL GUARDIA DE SEGURIDAD (PYDANTIC)
# ConfigParser necesita escapar los porcentajes de una URL codificada.
config.set_main_option("sqlalchemy.url", revision.DATABASE_URL.replace("%", "%%"))

target_metadata = miclaseBase.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # La transacción envuelve la ejecución; run_migrations no es un contexto.
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
