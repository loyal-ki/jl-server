from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import jwt
from pydantic import SecretStr

from app.config.config import Config

SecretType = Union[str, SecretStr]


def _get_secret_value(secret: SecretType) -> str:
    # Returns the secret value of the secret.
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: dict,
    secret: SecretType,
    audience: str,
    lifetime_days: Optional[int] = None,
    algorithm: str = Config.JWT_ALGORITHM,
) -> str:
    payload = data.copy()
    payload["aud"] = audience
    # Set the expiration time in seconds.
    if lifetime_days:
        expire = datetime.utcnow() + timedelta(days=lifetime_days)
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str,
    secret: SecretType,
    audience: List[str] = [
        Config.JWT_AUD_CREATE,
        Config.JWT_AUD_VERIFY,
        Config.JWT_AUD_RESET,
    ],
    algorithms: List[str] = [Config.JWT_ALGORITHM],
) -> Dict[str, Any]:
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
