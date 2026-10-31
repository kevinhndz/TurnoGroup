import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from database.almacen import miclaseBase
from backend.Empresas.tabla import Empresas
from backend.Sucursales.tabla import Sucursales
from backend.Usuarios.tabla import Usuarios
from backend.Categorias.tabla import Categorias
from backend.Productos.tabla import Productos
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.TiposServicio.tabla import TiposServicio
from backend.MetodosPago.tabla import MetodosPago
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.PagosSucursales.tabla import PagosSucursales
from backend.Mesas.tabla import Mesas
from backend.Pedidos.schema import Revisar_Json_Crear_Pedido
from backend.Pedidos.service import PedidoService
from backend.Cajas.schema import Revisar_Json_Abrir_Caja
from backend.Cajas.service import CajaService
from backend.Reservas.schema import Revisar_Json_Crear_Reserva
from backend.Reservas.service import ReservaService


@pytest.fixture
def base_concurrente():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url or not url.startswith("postgresql"):
        pytest.skip("La concurrencia requiere TEST_DATABASE_URL en PostgreSQL local")
    destino = make_url(url)
    assert destino.host in ("localhost", "127.0.0.1") and destino.database.endswith(
        "_pytest"
    )
    motor = create_engine(url)
    esquema = "prueba_" + uuid4().hex
    with motor.begin() as conexion:
        conexion.execute(text(f"CREATE SCHEMA {esquema}"))
    aislado = motor.execution_options(schema_translate_map={None: esquema})
    try:
        miclaseBase.metadata.create_all(aislado)
        with Session(aislado) as db:
            empresa = Empresas(
                nombre="Empresa concurrente",
                tipo_negocio="Otro",
                codigo_pais="HN",
                codigo_moneda="HNL",
                zona_horaria="America/Tegucigalpa",
            )
            usuario = Usuarios(nombre="Cajero", correo="concurrente@example.com")
            servicio = TiposServicio(
                clave_concepto="comer_aqui", nombre_visible="Comer aqui"
            )
            pago = MetodosPago(clave_concepto="efectivo", nombre_visible="Efectivo")
            db.add_all([empresa, usuario, servicio, pago])
            db.flush()
            sucursal = Sucursales(
                id_empresa=empresa.id,
                nombre="Principal",
                direccion="Direccion de prueba",
            )
            producto = Productos(id_empresa=empresa.id, nombre="Cafe", precio=45)
            db.add_all([sucursal, producto])
            db.flush()
            mesa = Mesas(id_sucursal=sucursal.id, nombre="Mesa 1", capacidad=4)
            db.add_all(
                [
                    mesa,
                    DisponibilidadProductos(
                        id_sucursal=sucursal.id, id_producto=producto.id
                    ),
                    ServiciosSucursales(
                        id_sucursal=sucursal.id,
                        id_tipo_servicio=servicio.id,
                        habilitado=True,
                        mesas_habilitadas=True,
                        reservas_habilitadas=True,
                    ),
                    PagosSucursales(
                        id_sucursal=sucursal.id, id_metodo_pago=pago.id, habilitado=True
                    ),
                ]
            )
            db.flush()
            ids = {
                "empresa": empresa.id,
                "sucursal": sucursal.id,
                "producto": producto.id,
                "usuario": usuario.id,
                "servicio": servicio.id,
                "pago": pago.id,
                "mesa": mesa.id,
            }
            db.commit()
        yield aislado, ids
    finally:
        with motor.begin() as conexion:
            conexion.execute(text(f"DROP SCHEMA {esquema} CASCADE"))
        motor.dispose()


@pytest.mark.parametrize("operacion", ["pedido", "caja", "reserva"])
def test_dos_solicitudes_no_duplican_operaciones(base_concurrente, operacion):
    motor, ids = base_concurrente
    barrera = Barrier(2)
    clave = uuid4()
    inicio = datetime.now(timezone.utc) + timedelta(days=2)

    def ejecutar():
        with Session(motor) as db:
            contexto = {
                "id_empresa": ids["empresa"],
                "id_sucursal": ids["sucursal"],
                "usuario": db.get(Usuarios, ids["usuario"]),
            }
            barrera.wait(timeout=10)
            try:
                if operacion == "pedido":
                    cuerpo = Revisar_Json_Crear_Pedido(
                        clave_operacion=clave,
                        id_tipo_servicio=ids["servicio"],
                        id_metodo_pago=ids["pago"],
                        detalles=[{"id_producto": ids["producto"], "cantidad": 1}],
                    )
                    return PedidoService.crear_service(cuerpo, db, contexto)["id"]
                if operacion == "caja":
                    return CajaService.abrir_service(
                        Revisar_Json_Abrir_Caja(monto_inicial=0), db, contexto
                    )["id"]
                cuerpo = Revisar_Json_Crear_Reserva(
                    id_mesa=ids["mesa"],
                    cliente="Prueba",
                    personas=2,
                    inicio=inicio,
                    fin=inicio + timedelta(hours=1),
                )
                return ReservaService.guardar_service(cuerpo, db, contexto)["id"]
            except HTTPException as error:
                db.rollback()
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as grupo:
        resultados = list(grupo.map(lambda _: ejecutar(), range(2)))
    if operacion == "pedido":
        assert resultados == [1, 1]
    else:
        assert sorted(resultados) == [1, 409]
