"""API aislada para Playwright. Nunca utiliza .env ni envia correos reales."""

import json
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
CARPETA = RAIZ / ".archivos" / "e2e"
BASE = CARPETA / "navegador.sqlite"
os.environ.update(
    {
        "TURNO_ENV": ".env.e2e-no-utilizado",
        "DATABASE_URL": "sqlite:///" + str(BASE),
        "ENTORNO": "pruebas",
        "SECRET_KEY": "clave-aislada-para-pruebas-de-navegador",
        "COOKIE_SEGURA": "true",
        "BACKEND_PROXY_SECRET": "proxy-aislado-para-pruebas-de-navegador",
        "ORIGENES_PERMITIDOS": '["https://127.0.0.1:18443"]',
        "URL_FRONTEND": "https://127.0.0.1:18443",
        "REDIS_URL": "",
        "CORREO_CLAVE_CIFRADO": "",
        "SMTP_SERVIDOR": "no-enviar.example.com",
        "SMTP_USUARIO": "pruebas",
        "SMTP_CLAVE": "pruebas",
        "SMTP_REMITENTE": "pruebas@example.com",
        "FACTURACION_MODO": "simulado",
        "ALTA_PUBLICA_HABILITADA": "true",
        "AUDITORIA_ARCHIVO": str(CARPETA / "auditoria.log"),
        "LIMITE_LOGIN": "100",
        "LIMITE_INVITACION": "100",
        "LIMITE_RECUPERACION": "100",
        "GEMINI_API_KEY": "",
    }
)


def preparar():
    CARPETA.mkdir(parents=True, exist_ok=True)
    BASE.unlink(missing_ok=True)
    from database.almacen import motor, llaves, miclaseBase
    import main
    from backend.Empresas.tabla import Empresas
    from backend.Sucursales.tabla import Sucursales
    from backend.Usuarios.tabla import Usuarios
    from backend.VinculosLaborales.tabla import (
        VinculosLaborales,
        AsignacionesSucursales,
    )
    from backend.Suscripciones.tabla import Suscripciones
    from backend.Categorias.tabla import Categorias
    from backend.Productos.tabla import Productos
    from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
    from backend.TiposServicio.tabla import TiposServicio
    from backend.MetodosPago.tabla import MetodosPago
    from backend.ServiciosSucursales.tabla import ServiciosSucursales
    from backend.PagosSucursales.tabla import PagosSucursales
    from backend.Correos.service import cifrador
    from utils.hash import encriptar_contrasena
    from utils.mfa import generar_codigos_respaldo
    import pyotp

    miclaseBase.metadata.create_all(motor)
    hash_clave = encriptar_contrasena("Clave-navegador123!")
    with llaves() as db:
        servicio = TiposServicio(
            clave_concepto="para_llevar", nombre_visible="Para llevar"
        )
        pago = MetodosPago(clave_concepto="efectivo", nombre_visible="Efectivo")
        db.add_all([servicio, pago])
        db.flush()
        for numero in (1, 2):
            empresa = Empresas(
                nombre=f"Cafeteria E2E {numero}",
                tipo_negocio="Otro",
                codigo_pais="HN",
                codigo_moneda="HNL",
                zona_horaria="America/Tegucigalpa",
            )
            db.add(empresa)
            db.flush()
            sucursal = Sucursales(
                id_empresa=empresa.id,
                nombre="Principal",
                direccion="Direccion de prueba",
                es_principal=True,
            )
            categoria = Categorias(id_empresa=empresa.id, nombre="Bebidas")
            db.add_all(
                [
                    sucursal,
                    categoria,
                    Suscripciones(id_empresa=empresa.id, finanzas_habilitadas=True),
                ]
            )
            db.flush()
            producto = Productos(
                id_empresa=empresa.id,
                id_categoria=categoria.id,
                nombre=f"Cafe E2E {numero}",
                precio=50,
            )
            db.add(producto)
            db.flush()
            db.add_all(
                [
                    DisponibilidadProductos(
                        id_sucursal=sucursal.id,
                        id_producto=producto.id,
                        disponible=True,
                    ),
                    ServiciosSucursales(
                        id_sucursal=sucursal.id,
                        id_tipo_servicio=servicio.id,
                        habilitado=True,
                    ),
                    PagosSucursales(
                        id_sucursal=sucursal.id, id_metodo_pago=pago.id, habilitado=True
                    ),
                ]
            )
            roles = (
                ["Gerente", "Administrador", "Mesero"] if numero == 1 else ["Gerente"]
            )
            for rol in roles:
                usuario = Usuarios(
                    nombre=f"{rol} E2E {numero}",
                    correo=f"{rol.lower()}{numero}@example.com",
                    clave_protegida=hash_clave,
                )
                db.add(usuario)
                db.flush()
                vinculo = VinculosLaborales(
                    id_usuario=usuario.id, id_empresa=empresa.id, rol=rol, activo=True
                )
                db.add(vinculo)
                db.flush()
                if rol != "Gerente":
                    db.add(
                        AsignacionesSucursales(
                            id_vinculo_laboral=vinculo.id, id_sucursal=sucursal.id
                        )
                    )
        secreto = pyotp.random_base32()
        plataforma = Usuarios(
            nombre="Plataforma E2E",
            correo="plataforma@example.com",
            rol_plataforma="Superadministrador",
            clave_protegida=hash_clave,
            mfa_secreto_cifrado=cifrador().encrypt(secreto.encode()).decode(),
        )
        db.add(plataforma)
        db.flush()
        respaldo = generar_codigos_respaldo(db, plataforma)[0]
        db.commit()
        descriptor = os.open(
            CARPETA / "mfa.json", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600
        )
        with os.fdopen(descriptor, "w") as archivo:
            json.dump({"secreto": secreto, "respaldo": respaldo}, archivo)
    # La cola queda pendiente para que el test lea el mensaje sin un servidor SMTP.
    import utils.correo

    utils.correo.enviar_verificacion = lambda correo, codigo: False
    utils.correo.enviar_invitacion = lambda correo, codigo: False
    utils.correo.enviar_recuperacion = lambda correo, codigo: False
    utils.correo.enviar_cambio_correo = lambda correo, codigo: False
    utils.correo.enviar_aviso_correo = lambda correo, codigo: False
    # Simulo solo el proveedor externo; conciliacion y guardado usan la API real.
    from backend.Productos import menu_ia
    from backend.Productos.menu_schema import ExtraccionMenu

    def leer_menu_prueba(solicitud, moneda):
        if solicitud.imagen:
            menu_ia.preparar_imagen(solicitud.imagen)
        productos = []
        for nombre, precio, categoria in (
            ("Cafe E2E 1", "50.00", "Bebidas"),
            ("Pan inteligente", None, "Panaderia IA"),
            ("Galleta inteligente", "8.00", "Panaderia IA"),
        ):
            productos.append(
                {
                    "nombre": nombre,
                    "precio": precio,
                    "categoria": categoria,
                    "descripcion": None,
                    "evidencia": nombre,
                    "advertencia": "Completa el precio" if precio is None else None,
                }
            )
        return ExtraccionMenu(productos=productos, advertencias=[]), {
            "tokens_in": 0,
            "tokens_out": 0,
        }

    menu_ia.extraer_menu = leer_menu_prueba
    return main.app


def leer_correo(correo, tipo):
    from database.almacen import llaves
    from backend.Correos.tabla import CorreosPendientes
    from backend.Correos.service import cifrador

    with llaves() as db:
        mensajes = (
            db.query(CorreosPendientes)
            .filter_by(tipo=tipo)
            .order_by(CorreosPendientes.id.desc())
            .all()
        )
        for mensaje in mensajes:
            if mensaje.contenido_cifrado:
                datos = json.loads(
                    cifrador().decrypt(mensaje.contenido_cifrado.encode())
                )
                if datos["correo"] == correo:
                    return datos["codigo"]
    raise SystemExit("No se encontro el correo de prueba")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "correo":
        print(leer_correo(sys.argv[2], sys.argv[3]))
    elif len(sys.argv) == 2 and sys.argv[1] == "respaldo":
        print(json.loads((CARPETA / "mfa.json").read_text())["respaldo"])
    else:
        import uvicorn

        uvicorn.run(preparar(), host="127.0.0.1", port=18080, access_log=False)
