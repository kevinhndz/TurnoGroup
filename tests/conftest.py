import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "clave-solo-para-pruebas")

from database.almacen import miclaseBase, abrir_puerta_bd
from main import app
from backend.Empresas.tabla import Empresas
from backend.Categorias.tabla import Categorias
from backend.Productos.tabla import Productos
from backend.Sucursales.tabla import Sucursales
from backend.Usuarios.tabla import Usuarios
from backend.TiposServicio.tabla import TiposServicio
from backend.MetodosPago.tabla import MetodosPago


@pytest.fixture
def db():
    url = os.environ.get("TEST_DATABASE_URL", "sqlite://")
    opciones = {}
    if url.startswith("sqlite"):
        opciones = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
    motor = create_engine(url, **opciones)
    if url.startswith("sqlite"):
        @event.listens_for(motor, "connect")
        def activar_claves(dbapi_connection, connection_record):
            dbapi_connection.execute("PRAGMA foreign_keys=ON")
    miclaseBase.metadata.create_all(motor)
    conexion = motor.connect()
    transaccion = conexion.begin()
    sesion = Session(bind=conexion, join_transaction_mode="create_savepoint")
    try:
        if sesion.query(TiposServicio).count() == 0:
            sesion.add_all([
                TiposServicio(clave_concepto="comer_aqui", nombre_visible="Comer aqui"),
                TiposServicio(clave_concepto="para_llevar", nombre_visible="Para llevar"),
                TiposServicio(clave_concepto="domicilio", nombre_visible="Domicilio"),
            ])
        if sesion.query(MetodosPago).count() == 0:
            sesion.add_all([
                MetodosPago(clave_concepto="efectivo", nombre_visible="Efectivo"),
                MetodosPago(clave_concepto="transferencia", nombre_visible="Transferencia"),
                MetodosPago(clave_concepto="tarjeta", nombre_visible="Tarjeta"),
            ])
        sesion.commit()
        yield sesion
    finally:
        sesion.close()
        transaccion.rollback()
        conexion.close()
        motor.dispose()


@pytest.fixture
def client(db):
    def abrir_base_pruebas():
        yield db
    app.dependency_overrides[abrir_puerta_bd] = abrir_base_pruebas
    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def datos(db):
    empresas = [Empresas(nombre="Empresa de prueba " + str(i), tipo_negocio="Otro",
                         codigo_pais="HN", codigo_moneda="HNL", zona_horaria="America/Tegucigalpa") for i in range(2)]
    db.add_all(empresas)
    db.flush()
    sucursales = [Sucursales(id_empresa=empresas[i].id, nombre="Local " + str(i), direccion="Direccion de prueba") for i in range(2)]
    categorias = [Categorias(id_empresa=empresas[i].id, nombre="Categoria " + str(i)) for i in range(2)]
    usuario = Usuarios(nombre="Persona de prueba", correo="persona@example.com")
    db.add_all(sucursales + categorias + [usuario])
    db.flush()
    productos = [Productos(id_empresa=empresas[i].id, id_categoria=categorias[i].id, nombre="Producto " + str(i), precio=75) for i in range(2)]
    db.add_all(productos)
    db.commit()
    return {"empresa": empresas[0].id, "otra_empresa": empresas[1].id,
            "sucursal": sucursales[0].id, "otra_sucursal": sucursales[1].id,
            "categoria": categorias[0].id, "otra_categoria": categorias[1].id,
            "producto": productos[0].id, "otro_producto": productos[1].id,
            "usuario": usuario.id}
