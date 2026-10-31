from getpass import getpass
from pydantic import EmailStr, TypeAdapter
from database.almacen import llaves
from backend.Usuarios.tabla import Usuarios
from utils.hash import encriptar_contrasena, verificar_contrasena


def crear_superadministrador():
    correo = str(TypeAdapter(EmailStr).validate_python(input("Correo: ").strip())).lower()
    clave = getpass("Clave (no se muestra): ")
    with llaves() as db:
        look_up = db.query(Usuarios).filter(Usuarios.correo == correo).first()
        if look_up:
            if not look_up.estado or not look_up.clave_protegida or not verificar_contrasena(clave, look_up.clave_protegida):
                print("No se pudo verificar la cuenta")
                return
        else:
            if not 12 <= len(clave) <= 128:
                print("La clave debe tener entre 12 y 128 caracteres")
                return
            nombre = input("Nombre: ").strip()
            if not 1 <= len(nombre) <= 100:
                print("Indica un nombre de hasta 100 caracteres")
                return
            look_up = Usuarios(correo=correo, nombre=nombre, clave_protegida=encriptar_contrasena(clave))
            db.add(look_up)
        look_up.rol_plataforma = "Superadministrador"
        db.flush()
        from backend.Usuarios.service import UsuarioService
        UsuarioService.revocar_accesos_service(look_up.id, db)
        db.commit()
        print("Superadministrador configurado")


if __name__ == "__main__":
    crear_superadministrador()
