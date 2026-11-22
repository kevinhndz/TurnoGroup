"""Configuracion local del autenticador: python -m scripts.configurar_mfa."""

from getpass import getpass
import pyotp
from backend.Usuarios.tabla import Usuarios
from backend.Sesiones.repository import SesionRepository
from database.almacen import llaves
from backend.Correos.service import cifrador
from utils.hash import verificar_contrasena
from utils.mfa import verificar_mfa
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
            verificar_mfa(usuario, getpass("Codigo del autenticador actual: "))
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
        db.commit()
        print(
            "Segundo factor activado. Espera al siguiente codigo para iniciar sesion."
        )


if __name__ == "__main__":
    main()
