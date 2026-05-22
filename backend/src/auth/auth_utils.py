import jwt
from jwt.exceptions import InvalidTokenError

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidCredentials


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            auth_settings.JWT_SECRET,
            algorithms=[auth_settings.JWT_ALG],
        )
    except InvalidTokenError:
        raise InvalidCredentials()
