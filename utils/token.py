from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from hashlib import sha256
from jose import JWTError, jwt
from core.config import revision as settings
from core.exceptions import AccesoProhibidoError

KEY = settings.SECRET_KEY


def crear_token(user: str, id_user: int, rol: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=20)

    data = {
        "user": user,
        "id_user": id_user,
        "rol": rol,
        "exp": expires
    }

    token = jwt.encode(data, KEY, algorithm=settings.ALGORITHM)

    return token


def verificar_token(token: str) -> dict:
    try:
        user_data = jwt.decode(
            token,
            KEY,
            algorithms=[settings.ALGORITHM],
            options={"require_exp": True}
        )
        return user_data

    except JWTError:
        raise AccesoProhibidoError("Token invalido o sesion expirada") from None


def crear_token_sesion() -> str:
    return token_urlsafe(32)


def proteger_token_sesion(token: str) -> str:
    return sha256(token.encode()).hexdigest()
