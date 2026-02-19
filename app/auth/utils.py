from typing import Union

import bcrypt
import hashlib


BytesLike = Union[str, bytes]


def _to_bytes(value: BytesLike) -> bytes:
    return value.encode("utf-8") if isinstance(value, str) else value


def hash_secret(value: BytesLike) -> bytes:
    raw: bytes = _to_bytes(value)
    return bcrypt.hashpw(raw, bcrypt.gensalt())


def verify_secret(hashed_value: bytes, value: BytesLike) -> bool:
    raw: bytes = _to_bytes(value)
    return bcrypt.checkpw(raw, hashed_value)


def hash_token(token: str) -> bytes:
    digest: bytes = hashlib.sha256(token.encode("utf-8")).digest()
    return hash_secret(value=digest)


def _verification_token(hashed_token: bytes, token: str) -> bool:
    digest: bytes = hashlib.sha256(token.encode("utf-8")).digest()
    return verify_secret(value=digest, hashed_value=hashed_token)

