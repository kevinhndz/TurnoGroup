import smtplib
import ssl
from email.message import EmailMessage
from core.config import revision


def enviar_recuperacion(correo: str, codigo: str) -> bool:
    mensaje = EmailMessage()
    mensaje["From"] = revision.SMTP_REMITENTE
    mensaje["To"] = correo
    mensaje["Subject"] = "Recuperar clave de Turno Group"
    mensaje.set_content(
        "Tu codigo de recuperacion es: " + codigo +
        "\nVence en 15 minutos y solo se puede usar una vez. "
        "Si no lo solicitaste, ignora este mensaje."
    )

    try:
        with smtplib.SMTP(revision.SMTP_SERVIDOR, revision.SMTP_PUERTO, timeout=10) as servidor:
            servidor.starttls(context=ssl.create_default_context())
            servidor.login(revision.SMTP_USUARIO, revision.SMTP_CLAVE)
            servidor.send_message(mensaje)
        return True
    except (OSError, smtplib.SMTPException):
        # No imprimir errores SMTP que puedan incluir secretos.
        return False


def enviar_invitacion(correo: str, codigo: str) -> bool:
    mensaje = EmailMessage()
    mensaje["From"] = revision.SMTP_REMITENTE
    mensaje["To"] = correo
    mensaje["Subject"] = "Invitacion laboral de Turno Group"
    mensaje.set_content("Inicia sesion con este correo y acepta la invitacion con este codigo: " + codigo +
                        "\nVence en 48 horas y solo puede usarse una vez. Si no la esperabas, ignorala.")
    try:
        with smtplib.SMTP(revision.SMTP_SERVIDOR, revision.SMTP_PUERTO, timeout=10) as servidor:
            servidor.starttls(context=ssl.create_default_context())
            servidor.login(revision.SMTP_USUARIO, revision.SMTP_CLAVE)
            servidor.send_message(mensaje)
        return True
    except (OSError, smtplib.SMTPException):
        return False
