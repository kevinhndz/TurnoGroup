"""Configuracion local del autenticador: python -m scripts.configurar_mfa."""

from getpass import getpass
import pyotp
from backend.Usuarios.tabla import Usuarios
from backend.Sesiones.repository import SesionRepository
from database.almacen import llaves
from backend.Correos.service import cifrador
from utils.hash import verificar_contrasena
from utils.mfa import verificar_segundo_factor, generar_codigos_respaldo
from datetime import datetime


def main():
    correo = input("Correo del superadministrador: ").strip().lower()
    clave = getpass("Contrasena actual: ")
    with llaves() as db:
        usuario = (
            db.query(Usuarios)
            .filter(Usuarios.correo == correo)
            .with_for_update()
            .first()
        )
        if (
            not usuario
            or not usuario.estado
            or usuario.rol_plataforma != "Superadministrador"
            or not usuario.clave_protegida
            or not verificar_contrasena(clave, usuario.clave_protegida)
        ):
            raise SystemExit("No se pudo verificar la cuenta")
        if usuario.mfa_secreto_cifrado:
            actual = getpass("Codigo del autenticador o codigo de respaldo: ").strip()
            verificar_segundo_factor(
                usuario,
                actual if len(actual) == 6 else None,
                actual if len(actual) != 6 else None,
                db,
            )
        secreto = pyotp.random_base32()
        print("Agrega esta clave manualmente a tu autenticador. No la compartas:")
        print(secreto)
        codigo = getpass("Codigo del autenticador nuevo: ")
        try:
            contador = pyotp.TOTP(secreto).verify_and_get_timecode(codigo)
        except pyotp.OTPVerificationError:
            raise SystemExit("Codigo incorrecto. No se guardo ningun cambio") from None
        usuario.mfa_secreto_cifrado = cifrador().encrypt(secreto.encode()).decode()
        usuario.mfa_ultimo_contador = contador
        SesionRepository.revocar_sesiones(db, usuario.id, datetime.utcnow())
        codigos = generar_codigos_respaldo(db, usuario)
        db.commit()
        print("Guarda estos codigos fuera del sistema. Cada uno sirve una sola vez:")
        for codigo_respaldo in codigos:
            print(codigo_respaldo)
        print(
            "Segundo factor activado. Espera al siguiente codigo para iniciar sesion."
        )


if __name__ == "__main__":
    main()
